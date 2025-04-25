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
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.hpc import HPCQueue
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.enums.inference.huggingface import BatchJobStatus
from math_rag.infrastructure.inference.partials import PartialBatchLLM
from math_rag.infrastructure.mappings.inference.huggingface import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.models.inference.huggingface import (
    BatchJob,
    BatchJobStatusTracker,
)
from math_rag.infrastructure.services import TGISettingsLoaderService
from math_rag.infrastructure.utils import (
    FileHasherUtil,
    FileReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)
from math_rag.infrastructure.validators.inference.huggingface import (
    HuggingFaceValidator,
)
from math_rag.shared.utils import DataclassMapperUtil


PBS_JOB_NAME = 'tgi'
LOCAL_ROOT_PATH = Path(__file__).parents[4]
REMOTE_ROOT_PATH = Path('tgi_default_root')

# must be greater than WALL_TIME_THRESHOLD in tgi.py
WALL_TIME_THRESHOLD = timedelta(minutes=10)

logger = getLogger(__name__)


class TGIBatchLLM(PartialBatchLLM):
    def __init__(
        self,
        file_system_client: FileSystemClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_client: ApptainerClient,
        tgi_settings_loader_service: TGISettingsLoaderService,
    ):
        self.file_system_client = file_system_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client
        self.apptainer_client = apptainer_client
        self.tgi_settings_loader_service = tgi_settings_loader_service

    async def init_resources(self):
        tmp_path = LOCAL_ROOT_PATH / '.tmp'
        hf_path = LOCAL_ROOT_PATH / 'assets/hpc/hf'
        tgi_path = hf_path / 'tgi'
        prometheus_path = LOCAL_ROOT_PATH / 'assets/hpc/prometheus'
        ngrok_path = LOCAL_ROOT_PATH / 'assets/hpc/ngrok'

        # NOTE: order matters, e.g. client.def requires requirements.txt to build client.sif
        local_paths = [
            hf_path / 'cli.def',
            tgi_path / 'requirements.txt',
            tgi_path / 'server.def',
            tgi_path / 'client.def',
            tgi_path / 'client.py',
            tgi_path / 'tgi.py',
            tgi_path / 'tgi.sh',
            prometheus_path / 'prometheus.yml',
            prometheus_path / 'prometheus.def',
            ngrok_path / 'ngrok.yml',
            ngrok_path / 'ngrok.def',
            LOCAL_ROOT_PATH / '.env.hpc.hf.tgi',
            LOCAL_ROOT_PATH / '.env.hpc.ngrok',
        ]

        for local_path in local_paths:
            assert local_path.exists()

        await self.file_system_client.make_directory(REMOTE_ROOT_PATH)

        for local_path in local_paths:
            remote_path = REMOTE_ROOT_PATH / local_path.name

            if await self.file_system_client.test(remote_path):
                local_hash = FileHasherUtil.hash(local_path, 'sha256')
                remote_hash = await self.file_system_client.hash(
                    remote_path, 'sha256sum'
                )

                if local_hash != remote_hash:
                    await self.file_system_client.remove(remote_path)

                    logger.info(f'Upload started: {local_path}')

                else:
                    logger.info(f'Upload skipped: {local_path} unchanged')
                    continue

            if local_path.suffix == '.def':
                match local_path.name:
                    case 'client.def':
                        additional_path = tgi_path / 'requirements.txt'

                    case 'prometheus.def':
                        additional_path = prometheus_path / 'prometheus.yml'

                    case 'ngrok.def':
                        additional_path = ngrok_path / 'ngrok.yml'

                    case _:
                        additional_path = None

                sif_stream = await self.apptainer_client.build(
                    local_path, additional_path
                )

                sif_local_path = tmp_path / f'{local_path.stem}.sif'
                await FileStreamWriterUtil.write(sif_stream, sif_local_path)

                sif_remote_path = REMOTE_ROOT_PATH / sif_local_path.name

                if await self.file_system_client.test(sif_remote_path):
                    await self.file_system_client.remove(sif_remote_path)

                await self.sftp_client.upload(sif_local_path, sif_remote_path)

            await self.sftp_client.upload(local_path, remote_path)

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        *,
        max_tokens_per_day: float | None,
    ) -> str:
        # validate
        if max_tokens_per_day is not None:
            raise ValueError(
                f'{self.__class__.__name__} does not support max_tokens_per_day'
            )

        model = batch_request.requests[0].params.model
        HuggingFaceValidator.validate_model_name(model)

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
        input_jsonl_str = '\n'.join(lines)
        input_jsonl_bytes = input_jsonl_str.encode('utf-8')

        # write input file
        input_local_path = LOCAL_ROOT_PATH / '.tmp' / f'input_{batch_request.id}.jsonl'
        await FileWriterUtil.write(input_jsonl_bytes, input_local_path)

        # upload input file and avoid race-conditions
        input_remote_path = REMOTE_ROOT_PATH / input_local_path.name
        input_remote_part_path = input_remote_path.with_name(
            input_remote_path.name + '.part'
        )
        await self.sftp_client.upload(input_local_path, input_remote_part_path)
        await self.file_system_client.move(input_remote_part_path, input_remote_path)

        # select job by name or create a new one
        job_id = await self.pbs_pro_client.queue_select(PBS_JOB_NAME)

        if job_id:
            try:
                (
                    wall_time,
                    wall_time_used,
                ) = await self.pbs_pro_client.queue_status_wall_times(job_id)

                if wall_time_used is None:
                    raise ValueError(
                        'Wall time used can not be None because job is running'
                    )

                wall_time_left = wall_time - wall_time_used

            except Exception as e:
                logger.error(
                    f'Failed to get wall time because job {job_id} terminated: {e}'
                )
                wall_time_left = None

            if not wall_time_left or wall_time_left < WALL_TIME_THRESHOLD:
                tgi_settings = self.tgi_settings_loader_service.load(model)
                job_id = await self.pbs_pro_client.queue_submit(
                    REMOTE_ROOT_PATH,
                    PBS_JOB_NAME,
                    num_chunks=tgi_settings.num_chunks,
                    num_cpus=tgi_settings.num_cpus,
                    num_gpus=tgi_settings.num_gpus,
                    mem=tgi_settings.mem,
                    wall_time=tgi_settings.wall_time,
                    depend_job_id=job_id,
                    queue=HPCQueue.GPU_TEST,  # TODO remove
                )

        else:
            tgi_settings = self.tgi_settings_loader_service.load(model)
            job_id = await self.pbs_pro_client.queue_submit(
                REMOTE_ROOT_PATH,
                PBS_JOB_NAME,
                num_chunks=tgi_settings.num_chunks,
                num_cpus=tgi_settings.num_cpus,
                num_gpus=tgi_settings.num_gpus,
                mem=tgi_settings.mem,
                wall_time=tgi_settings.wall_time,
                queue=HPCQueue.GPU_TEST,  # TODO remove
            )

        job = await self.pbs_pro_client.queue_status(job_id)
        logger.info(
            f'Job {job_id} obtained for '
            f'batch request {batch_request.id} '
            f'with state {job.state}'
        )

        # create in-memory batch job file
        batch_job = BatchJob(
            batch_request_id=batch_request.id,
            model_hub_id=model,
            timestamp=int(datetime.now().timestamp()),
        )
        batch_job_json_str = batch_job.model_dump_json()
        batch_job_json_bytes = batch_job_json_str.encode('utf-8')

        # write batch job file
        batch_job_local_path = (
            LOCAL_ROOT_PATH / '.tmp' / f'batch_job_{job_id}_{batch_request.id}.json'
        )
        await FileWriterUtil.write(batch_job_json_bytes, batch_job_local_path)

        # upload batch job file and avoid race-conditions
        batch_job_remote_path = REMOTE_ROOT_PATH / batch_job_local_path.name
        batch_job_remote_part_path = batch_job_remote_path.with_name(
            batch_job_remote_path.name + '.part'
        )
        await self.sftp_client.upload(batch_job_local_path, batch_job_remote_part_path)
        await self.file_system_client.move(
            batch_job_remote_part_path, batch_job_remote_path
        )

        return job_id

    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType] | None:
        job = await self.pbs_pro_client.queue_status(batch_id)
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

        status_tracker_remote_path = (
            REMOTE_ROOT_PATH / f'status_tracker_{batch_id}.json'
        )
        status_tracker_json = await self.file_system_client.concatenate(
            status_tracker_remote_path
        )
        status_tracker = BatchJobStatusTracker.model_validate_json(status_tracker_json)

        if batch_request_id not in status_tracker.id_to_status:
            return None

        status = status_tracker.id_to_status[batch_request_id]

        match status:
            case BatchJobStatus.WAITING | BatchJobStatus.RUNNING:
                return None

            case BatchJobStatus.FINISHED | BatchJobStatus.UNFINISHED:
                pass

        input_local_path = LOCAL_ROOT_PATH / '.tmp' / f'input_{batch_request_id}.jsonl'
        output_local_path = (
            LOCAL_ROOT_PATH / '.tmp' / f'output_{batch_request_id}.jsonl'
        )
        input_remote_path = REMOTE_ROOT_PATH / input_local_path.name
        output_remote_path = REMOTE_ROOT_PATH / output_local_path.name

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
                completion = DataclassMapperUtil.from_dict(
                    ChatCompletionOutput, response
                )
                response_list = LLMResponseListMapping[LLMResponseType].to_source(
                    completion,
                    request_id=request_id,
                    input_id=request.params.metadata['input_id'],
                    response_type=response_type,
                )
                response_lists.append(response_list)

        # find unfinished requests
        failed_request_ids = [
            failed_request.request.id for failed_request in failed_requests
        ]
        finished_request_ids = [
            response_list.request_id for response_list in response_lists
        ]
        finished_request_ids.extend(failed_request_ids)
        unfinished_request_ids = [
            request_id
            for request_id in requests_dict.keys()
            if request_id not in finished_request_ids
        ]

        for request_id in unfinished_request_ids:
            failed_request = LLMFailedRequest(
                request=requests_dict[request_id],
                errors=[],
            )
            failed_requests.append(failed_request)

        batch_result = LLMBatchResult(
            batch_request_id=batch_request_id,
            response_lists=response_lists,
            failed_requests=failed_requests,
        )

        await self.file_system_client.remove([input_remote_path, output_remote_path])
        input_local_path.unlink()
        output_local_path.unlink()

        return batch_result
