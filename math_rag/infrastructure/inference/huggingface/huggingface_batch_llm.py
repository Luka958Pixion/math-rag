import json

from datetime import timedelta
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
from math_rag.infrastructure.inference.partials import PartialBatchLLM
from math_rag.infrastructure.mappings.inference.huggingface import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.utils import (
    FileStreamReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)


logger = getLogger(__name__)


class HuggingFaceBatchLLM(PartialBatchLLM):
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
        local_paths = [
            tgi_path / 'tgi_server.def',
            tgi_path / 'tgi_client.def',
            hf_path / 'hf_cli.def',
            tgi_path / 'tgi.py',
            tgi_path / 'tgi.sh',
            tgi_path / 'requirements.txt',
            self.local_project_root / '.env.hpc.hf.tgi',
        ]

        for local_path in local_paths:
            assert local_path.exists()

        await self.hpc_client.make_directory(self.remote_project_root)

        for local_path in local_paths:
            remote_path = self.remote_project_root / local_path.name

            if await self.hpc_client.has_file_path(remote_path):
                if not await self.hpc_client.has_file_changed(local_path, remote_path):
                    logger.info(f'Upload skipped: {local_path} unchanged')
                    continue

                await self.hpc_client.remove_file(remote_path)

            logger.info(f'Upload started: {local_path}')
            await self.sftp_client.upload(local_path, remote_path)

            if local_path.suffix == '.def':
                sif_stream = await self.apptainer_client.build(local_path)

                sif_local_path = tmp_path / f'{local_path.stem}.sif'
                await FileStreamWriterUtil.write(sif_stream, sif_local_path)

                sif_remote_path = self.remote_project_root / sif_local_path.name
                await self.sftp_client.upload(sif_local_path, sif_remote_path)

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        request_dicts = [
            {
                'request_id': str(request.id),
                'request': LLMRequestMapping[LLMResponseType].to_target(request),
            }
            for request in batch_request.requests
        ]
        lines = [
            json.dumps(request_dict, separators=(',', ':'))
            for request_dict in request_dicts
        ]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')

        input_local_path = self.local_project_root / '.tmp' / 'input.jsonl'
        await FileWriterUtil.write(jsonl_bytes, input_local_path)

        input_remote_path = self.remote_project_root / input_local_path.name
        await self.sftp_client.upload(input_local_path, input_remote_path)

        pbs_path = Path('tgi.sh')
        env_vars = {'MODEL_HUB_ID': batch_request.requests[0].params.model}
        batch_id = await self.pbs_pro_client.queue_submit(
            self.remote_project_root,
            pbs_path,
            env_vars,
            num_chunks=1,
            num_cpus=8,
            num_gpus=1,
            mem=32 * 1024**3,
            walltime=timedelta(minutes=60),
        )
        status = await self.pbs_pro_client.queue_status(batch_id)

        logger.info(f'Batch {batch_id} created with state {status.state}')

        return batch_id

    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMBatchResult[LLMResponseType] | None:
        status = await self.pbs_pro_client.queue_status(batch_id)

        logger.info(f'Batch {batch_id} state {status.state}')

        match status.state:
            case (
                PBSProJobState.BEGUN
                | PBSProJobState.QUEUED
                | PBSProJobState.RUNNING
                | PBSProJobState.EXITING
                | PBSProJobState.WAITING
                | PBSProJobState.TRANSITING
                | PBSProJobState.SUSPENDED
                | PBSProJobState.USER_SUSPENDED
                | PBSProJobState.HELD
                | PBSProJobState.MOVED
            ):
                return None

            case PBSProJobState.FINISHED | PBSProJobState.EXITED:
                pass

        input_path = self.remote_project_root / 'input.jsonl'
        output_path = self.remote_project_root / 'output.jsonl'

        input_file_stream = await self.sftp_client.download(input_path, None)
        output_file_stream = await self.sftp_client.download(output_path, None)

        input_stream = FileStreamReaderUtil.read_jsonl(input_file_stream)
        output_stream = FileStreamReaderUtil.read_jsonl(output_file_stream)

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
            response = data['response']

            if response is None:
                error = LLMErrorMapping.to_source(data['error'])
                failed_request = LLMFailedRequest(
                    request=request,
                    errors=[error],
                )
                failed_requests.append(failed_request)

            else:
                completion = ChatCompletionOutput(**response)
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

        await self.hpc_client.remove_files([input_path, output_path])

        return batch_result
