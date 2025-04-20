import json

from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from uuid import UUID

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchResult,
    EMFailedRequest,
    EMRequest,
    EMResponseList,
)
from math_rag.infrastructure.clients import (
    ApptainerClient,
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.constants.inference.huggingface import (
    DEFAULT_TGI_SETTINGS,  # TODO
)
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.enums.inference.huggingface import BatchJobStatus
from math_rag.infrastructure.inference.partials import PartialBatchEM
from math_rag.infrastructure.mappings.inference.huggingface import (
    EMErrorMapping,
    EMRequestMapping,
    EMResponseListMapping,
)
from math_rag.infrastructure.models.inference.huggingface import (
    BatchJob,
    BatchJobStatusTracker,
)
from math_rag.infrastructure.utils import (
    FileHasherUtil,
    FileReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)


PBS_JOB_NAME = 'tei'
LOCAL_ROOT_PATH = Path(__file__).parents[4]
REMOTE_ROOT_PATH = Path('tei_default_root')

# must be greater than WALLTIME_THRESHOLD in tei.py
WALLTIME_THRESHOLD = timedelta(minutes=10)

logger = getLogger(__name__)


class TGIBatchEM(PartialBatchEM):
    def __init__(
        self,
        file_system_client: FileSystemClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_client: ApptainerClient,
    ):
        self.file_system_client = file_system_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client
        self.apptainer_client = apptainer_client

    async def init_resources(self):
        tmp_path = LOCAL_ROOT_PATH / '.tmp'
        hf_path = LOCAL_ROOT_PATH / 'assets/hpc/hf'
        tei_path = hf_path / 'tei'

        # NOTE: order matters, e.g. client.def requires requirements.txt to build client.sif
        local_paths = [
            hf_path / 'cli.def',
            tei_path / 'requirements.txt',
            tei_path / 'server.def',
            tei_path / 'client.def',
            tei_path / 'client.py',
            tei_path / 'tei.py',
            tei_path / 'tei.sh',
            LOCAL_ROOT_PATH / '.env.hpc.hf.tei',
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
                sif_stream = await self.apptainer_client.build(
                    local_path,
                    tei_path / 'requirements.txt'
                    if local_path.name == 'client.def'
                    else None,
                )

                sif_local_path = tmp_path / f'{local_path.stem}.sif'
                await FileStreamWriterUtil.write(sif_stream, sif_local_path)

                sif_remote_path = REMOTE_ROOT_PATH / sif_local_path.name

                if await self.file_system_client.test(sif_remote_path):
                    await self.file_system_client.remove(sif_remote_path)

                await self.sftp_client.upload(sif_local_path, sif_remote_path)

            await self.sftp_client.upload(local_path, remote_path)

    async def batch_embed_init(
        self,
        batch_request: EMBatchRequest,
    ) -> str:
        # map requests
        request_dicts = [
            {
                'request_id': str(request.id),
                'request': EMRequestMapping.to_target(request),
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
                    walltime,
                    walltime_used,
                ) = await self.pbs_pro_client.queue_status_walltimes(job_id)

                if walltime_used is None:
                    raise ValueError(
                        'Walltime used can not be None because job is running'
                    )

                walltime_left = walltime - walltime_used

            except Exception as e:
                logger.error(
                    f'Failed to get walltime because job {job_id} terminated: {e}'
                )
                walltime_left = None

            if not walltime_left or walltime_left < WALLTIME_THRESHOLD:
                job_id = await self.pbs_pro_client.queue_submit(
                    REMOTE_ROOT_PATH,
                    PBS_JOB_NAME,
                    num_chunks=DEFAULT_TGI_SETTINGS.num_chunks,
                    num_cpus=DEFAULT_TGI_SETTINGS.num_cpus,
                    num_gpus=DEFAULT_TGI_SETTINGS.num_gpus,
                    mem=DEFAULT_TGI_SETTINGS.mem,
                    walltime=DEFAULT_TGI_SETTINGS.walltime,
                    depend_job_id=job_id,
                )

        else:
            job_id = await self.pbs_pro_client.queue_submit(
                REMOTE_ROOT_PATH,
                PBS_JOB_NAME,
                num_chunks=DEFAULT_TGI_SETTINGS.num_chunks,
                num_cpus=DEFAULT_TGI_SETTINGS.num_cpus,
                num_gpus=DEFAULT_TGI_SETTINGS.num_gpus,
                mem=DEFAULT_TGI_SETTINGS.mem,
                walltime=DEFAULT_TGI_SETTINGS.walltime,
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
            model_hub_id=batch_request.requests[0].params.model,
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

    async def batch_embed_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> EMBatchResult | None:
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

        requests_dict: dict[UUID, EMRequest] = {}

        async for data in input_stream:
            request_id = UUID(data['request_id'])
            request = EMRequestMapping.to_source(
                data['request'],
                request_id=request_id,
            )

            requests_dict[request_id] = request

        failed_requests: list[EMFailedRequest] = []
        response_lists: list[EMResponseList] = []

        async for data in output_stream:
            request_id = UUID(data['request_id'])
            request = requests_dict[request_id]
            response: dict | None = data['response']

            if response is None:
                error = EMErrorMapping.to_source(data['error'])
                failed_request = EMFailedRequest(
                    request=request,
                    errors=[error],
                )
                failed_requests.append(failed_request)

            else:
                response_list = EMResponseListMapping.to_source(
                    response,
                    request_id=request_id,
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
            failed_request = EMFailedRequest(
                request=requests_dict[request_id],
                errors=[],
            )
            failed_requests.append(failed_request)

        batch_result = EMBatchResult(
            batch_request_id=batch_request_id,
            response_lists=response_lists,
            failed_requests=failed_requests,
        )

        await self.file_system_client.remove([input_remote_path, output_remote_path])
        input_local_path.unlink()
        output_local_path.unlink()

        return batch_result
