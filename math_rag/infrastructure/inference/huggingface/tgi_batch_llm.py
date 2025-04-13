import json

from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from uuid import UUID

from huggingface_hub.inference._generated.types import ChatCompletionOutput

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.clients import (
    ApptainerClient,
    HPCClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.enums.inference.huggingface import BatchJobStatus
from math_rag.infrastructure.inference.partials import PartialBatchLLM
from math_rag.infrastructure.mappings.inference.huggingface import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.utils import (
    FileReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)
from math_rag.shared.utils import DataclassUtil


JOB_NAME = 'tgi'

logger = getLogger(__name__)


class TGIBatchLLM(PartialBatchLLM):
    def __init__(
        self,
        remote_project_root: Path,
        hpc_client: HPCClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_client: ApptainerClient,
    ):
        self.local_project_root = Path(__file__).parents[4]
        self.remote_project_root = remote_project_root

        self.hpc_client = hpc_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client
        self.apptainer_client = apptainer_client

    async def init_resources(self):
        tmp_path = self.local_project_root / '.tmp'
        hf_path = self.local_project_root / 'assets/hpc/hf'
        tgi_path = hf_path / 'tgi'

        # NOTE: order matters, e.g. tgi_client.def requires requirements.txt to build tgi_client.sif
        local_paths = [
            hf_path / 'cli.def',
            tgi_path / 'requirements.txt',
            tgi_path / 'tgi_server.def',
            tgi_path / 'tgi_client.def',
            tgi_path / 'tgi_client.py',
            tgi_path / 'tgi.py',
            tgi_path / 'tgi.sh',
            tgi_path / 'status.json',
            self.local_project_root / '.env.hpc.hf.tgi',
        ]

        for local_path in local_paths:
            assert local_path.exists()

        await self.hpc_client.make_directory(self.remote_project_root)

        for local_path in local_paths:
            remote_path = self.remote_project_root / local_path.name

            if await self.hpc_client.has_file_path(remote_path):
                if await self.hpc_client.has_file_changed(local_path, remote_path):
                    await self.hpc_client.remove_file(remote_path)

                    logger.info(f'Upload started: {local_path}')

                else:
                    logger.info(f'Upload skipped: {local_path} unchanged')
                    continue

            if local_path.suffix == '.def':
                sif_stream = await self.apptainer_client.build(
                    local_path,
                    tgi_path / 'requirements.txt'
                    if local_path.name == 'tgi_client.def'
                    else None,
                )

                sif_local_path = tmp_path / f'{local_path.stem}.sif'
                await FileStreamWriterUtil.write(sif_stream, sif_local_path)

                sif_remote_path = self.remote_project_root / sif_local_path.name

                if await self.hpc_client.has_file_path(sif_remote_path):
                    await self.hpc_client.remove_file(sif_remote_path)

                await self.sftp_client.upload(sif_local_path, sif_remote_path)

            await self.sftp_client.upload(local_path, remote_path)

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        # map requests
        request_dicts = [
            {
                'request_id': str(request.id),
                'request': LLMRequestMapping[LLMResponseType].to_target(request),
            }
            for request in batch_request.requests
        ]

        # create in-memory input file
        lines = [
            json.dumps(request_dict, separators=(',', ':'))
            for request_dict in request_dicts
        ]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')

        # write input file
        input_local_path = (
            self.local_project_root / '.tmp' / f'input_{batch_request.id}.jsonl'
        )
        await FileWriterUtil.write(jsonl_bytes, input_local_path)

        # upload input file and avoid race-conditions
        input_remote_path = self.remote_project_root / input_local_path.name
        input_remote_part_path = input_remote_path.with_name(
            input_remote_path.name + '.part'
        )
        await self.sftp_client.upload(input_local_path, input_remote_part_path)
        await self.hpc_client.move(input_remote_part_path, input_remote_path)

        # create in-memory batch job file
        batch_job = {
            'batch_request_id': str(batch_request.id),
            'model_hub_id': batch_request.requests[0].params.model,
            'timestamp': int(datetime.now().timestamp()),
        }
        json_str = json.dumps(batch_job)
        json_bytes = json_str.encode('utf-8')

        # write batch job file
        batch_job_local_path = (
            self.local_project_root / '.tmp' / f'metadata_{batch_request.id}.json'
        )
        await FileWriterUtil.write(json_bytes, batch_job_local_path)

        # upload batch job file and avoid race-conditions
        batch_job_remote_path = self.remote_project_root / batch_job_local_path.name
        batch_job_remote_part_path = batch_job_remote_path.with_name(
            batch_job_remote_path.name + '.part'
        )
        await self.sftp_client.upload(batch_job_local_path, batch_job_remote_path)
        await self.hpc_client.move(batch_job_remote_part_path, batch_job_remote_path)

        # select job by name or create a new one
        job_id = self.pbs_pro_client.queue_select(JOB_NAME)

        if not job_id:
            job_id = await self.pbs_pro_client.queue_submit(
                self.remote_project_root,
                JOB_NAME,
                num_chunks=1,
                num_cpus=8,
                num_gpus=1,
                mem=32 * 1024**3,
                walltime=timedelta(minutes=60),  # TODO how to determine these params
            )

        job = await self.pbs_pro_client.queue_status(job_id)

        logger.info(
            f'Job {job_id} obtained for batch {batch_request.id} with state {job.state}'
        )

        return job_id

    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMBatchResult[LLMResponseType] | None:
        job_id = self.pbs_pro_client.queue_select(JOB_NAME)
        job = await self.pbs_pro_client.queue_status(job_id)

        logger.info(f'Batch {batch_id} state {job.state}')

        match job.state:
            case (
                PBSProJobState.BEGUN
                | PBSProJobState.QUEUED
                | PBSProJobState.EXITING
                | PBSProJobState.WAITING
                | PBSProJobState.TRANSITING
                | PBSProJobState.SUSPENDED
                | PBSProJobState.USER_SUSPENDED
                | PBSProJobState.HELD
                | PBSProJobState.MOVED
            ):
                return None

            case (
                PBSProJobState.RUNNING
                | PBSProJobState.FINISHED
                | PBSProJobState.EXITED
            ):
                pass

        status_remote_path = self.remote_project_root / 'status.jsonl'
        status_json = await self.hpc_client.concatenate(status_remote_path)
        status_dict: dict = json.loads(status_json)
        batch_id_to_status = {
            UUID(key): BatchJobStatus(value) for key, value in status_dict.items()
        }

        if batch_id not in batch_id_to_status:
            return None

        if batch_id_to_status[batch_id] == BatchJobStatus.RUNNING:
            return None

        input_local_path = self.local_project_root / '.tmp' / 'input.jsonl'
        output_local_path = self.local_project_root / '.tmp' / 'output.jsonl'
        input_remote_path = self.remote_project_root / 'output.jsonl'
        output_remote_path = self.remote_project_root / 'output.jsonl'

        await self.sftp_client.download(output_remote_path, output_local_path)

        input_stream = FileReaderUtil.read_jsonl(input_local_path)
        output_stream = FileReaderUtil.read_jsonl(output_local_path)

        requests_dict: dict[UUID, LLMRequest[LLMResponseType]] = {}

        async for data in input_stream:
            request_id = UUID(data['request_id'])
            request = LLMRequestMapping[LLMResponseType].to_source(
                data['request'],
                request_id=request_id,
                response_type=response_type,
            )

            requests_dict[request_id] = request

        failed_requests: list[LLMFailedRequest[LLMResponseType]] = []
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        async for data in output_stream:
            request_id = UUID(data['request_id'])
            request = requests_dict[request_id]
            response: dict | None = data['response']

            if response is None:
                error = LLMErrorMapping.to_source(data['error'])
                failed_request = LLMFailedRequest(
                    request=request,
                    errors=[error],
                )
                failed_requests.append(failed_request)

            else:
                response.pop('object')
                completion = DataclassUtil.from_dict(ChatCompletionOutput, response)
                response_list = LLMResponseListMapping[LLMResponseType].to_source(
                    completion,
                    request_id=request_id,
                    input_id=request.params.metadata['input_id'],
                    response_type=response_type,
                )
                response_lists.append(response_list)

        batch_result = LLMBatchResult(
            response_lists=response_lists, failed_requests=failed_requests
        )

        await self.hpc_client.remove_files([input_remote_path, output_remote_path])
        input_local_path.unlink()
        output_local_path.unlink()

        return batch_result
