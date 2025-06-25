import json

from asyncio import sleep
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
from math_rag.infrastructure.base import BaseInitializer
from math_rag.infrastructure.clients import (
    ApptainerClient,
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.hpc import HPCQueue
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
from math_rag.infrastructure.services import PBSProResourceListLoaderService
from math_rag.infrastructure.utils import (
    FileHasherUtil,
    FileReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)
from math_rag.infrastructure.validators.inference.huggingface import HuggingFaceModelNameValidator


PBS_JOB_NAME = 'tei'
LOCAL_ROOT_PATH = Path(__file__).parents[4]
REMOTE_ROOT_PATH = Path('tei_default_root')

# must be greater than WALL_TIME_THRESHOLD in tei.py
WALL_TIME_THRESHOLD = timedelta(minutes=10)
STATUS_TRACKER_DELAY = 30

logger = getLogger(__name__)


class TEIBatchEM(BaseInitializer, PartialBatchEM):
    def __init__(
        self,
        file_system_client: FileSystemClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_client: ApptainerClient,
        pbs_pro_resource_list_loader_service: PBSProResourceListLoaderService,
    ):
        self.file_system_client = file_system_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client
        self.apptainer_client = apptainer_client
        self.pbs_pro_resource_list_loader_service = pbs_pro_resource_list_loader_service

    async def _has_file_changed(self, local_path: Path, remote_path: Path) -> bool:
        """
        Determines whether a local file differs from its remote counterpart based on SHA-256 hash comparison.

        Computes the SHA-256 hash of both the local and remote files and compares them.

        Args:
            local_path (Path): Path to the local file.
            remote_path (Path): Path to the remote file.

        Returns:
            bool: True if the local and remote file hashes differ, False otherwise.
        """

        local_hash = FileHasherUtil.hash(local_path, 'sha256')
        remote_hash = await self.file_system_client.hash(remote_path, 'sha256sum')

        return local_hash != remote_hash

    async def _upload_file(self, local_path: Path, remote_path: Path, force: bool = False) -> bool:
        """
        Uploads a file to the remote path if it is missing or has changed.

        If the remote file exists:
            - Reuploads the file if `force` is True or the local file content differs.
            - Skips upload if the file is unchanged and `force` is False.

        If the remote file does not exist, uploads it directly.

        Args:
            local_path (Path): Path to the local file to upload.
            remote_path (Path): Destination path on the remote system.
            force (bool, optional): If True, reupload the file regardless of changes. Defaults to False.

        Returns:
            bool: True if the file was uploaded or reuploaded, False if upload was skipped.
        """

        if await self.file_system_client.test(remote_path):
            if force or await self._has_file_changed(local_path, remote_path):
                await self.file_system_client.remove(remote_path)
                await self.sftp_client.upload(local_path, remote_path)
                logger.info(f'Reupload completed: {remote_path}')

                return True

            else:
                logger.info(f'Upload skipped: {local_path} unchanged')

                return False

        else:
            await self.sftp_client.upload(local_path, remote_path)
            logger.info(f'Upload completed: {remote_path}')

            return True

    async def initialize(self):
        # common directory paths
        tmp_path = LOCAL_ROOT_PATH / '.tmp'
        hf_path = LOCAL_ROOT_PATH / 'assets/hpc/hf'
        tei_path = hf_path / 'tei'

        # build paths
        cli_def_path = hf_path / 'cli.def'
        requirements_txt_path = tei_path / 'requirements.txt'
        server_def_path = tei_path / 'server.def'
        client_def_path = tei_path / 'client.def'

        build_local_paths_dict: dict[Path, Path | None] = {
            cli_def_path: None,
            client_def_path: requirements_txt_path,
            server_def_path: None,
        }

        # runtime paths
        env_path = LOCAL_ROOT_PATH / '.env.hpc'
        client_py_path = tei_path / 'client.py'
        tei_py_path = tei_path / 'tei.py'
        tei_sh_path = tei_path / 'tei.sh'

        runtime_local_paths = [env_path, client_py_path, tei_py_path, tei_sh_path]

        # verify local paths
        local_paths = (
            runtime_local_paths
            + [key for key in build_local_paths_dict.keys()]
            + [value for value in build_local_paths_dict.values() if value is not None]
        )

        for local_path in local_paths:
            assert local_path.exists()

        # create remote root directory
        await self.file_system_client.make_directory(REMOTE_ROOT_PATH)

        # create remote data directory for prometheus
        await self.file_system_client.make_directory(REMOTE_ROOT_PATH / 'data')

        for def_local_path, additional_local_path in build_local_paths_dict.items():
            is_build_required = False
            is_build_required_additional = False

            # upload additional file
            if additional_local_path:
                additional_remote_path = REMOTE_ROOT_PATH / additional_local_path.name
                is_build_required_additional = await self._upload_file(
                    additional_local_path, additional_remote_path
                )

            # upload definition file
            def_remote_path = REMOTE_ROOT_PATH / def_local_path.name
            is_build_required = await self._upload_file(def_local_path, def_remote_path)

            # (re)build and (re)upload singularity image file
            if not is_build_required and not is_build_required_additional:
                continue

            sif_stream = await self.apptainer_client.build(def_local_path, additional_local_path)

            sif_local_path = tmp_path / f'{def_local_path.stem}.sif'
            await FileStreamWriterUtil.write(sif_stream, sif_local_path)

            # force upload to skip hashing for large images (hash always differs here)
            sif_remote_path = REMOTE_ROOT_PATH / sif_local_path.name
            await self._upload_file(sif_local_path, sif_remote_path, force=True)

        # upload runtime paths
        for local_path in runtime_local_paths:
            remote_path = REMOTE_ROOT_PATH / local_path.name
            await self._upload_file(local_path, remote_path)

    async def batch_embed_init(
        self,
        batch_request: EMBatchRequest,
        *,
        max_tokens_per_day: float | None,
        max_input_file_size: int | None,
    ) -> str:
        # validate
        if max_tokens_per_day is not None:
            raise ValueError(f'{self.__class__.__name__} does not support max_tokens_per_day')

        if max_input_file_size is not None:
            raise ValueError(f'{self.__class__.__name__} does not support max_input_file_size')

        if not batch_request.requests:
            raise ValueError(f'Batch request {batch_request.id} is empty')

        model = batch_request.requests[0].params.model
        HuggingFaceModelNameValidator.validate(model)

        # map requests
        request_dicts = [
            {
                'request_id': str(request.id),
                'request': EMRequestMapping.to_target(request),
            }
            for request in batch_request.requests
        ]

        # create in-memory input file
        lines = [json.dumps(request_dict, separators=(',', ':')) for request_dict in request_dicts]
        input_jsonl_str = '\n'.join(lines)
        input_jsonl_bytes = input_jsonl_str.encode('utf-8')

        # write input file
        input_local_path = LOCAL_ROOT_PATH / '.tmp' / f'input_{batch_request.id}.jsonl'
        await FileWriterUtil.write(input_jsonl_bytes, input_local_path)

        # upload input file and avoid race-conditions
        input_remote_path = REMOTE_ROOT_PATH / input_local_path.name
        input_remote_part_path = input_remote_path.with_name(input_remote_path.name + '.part')
        await self.sftp_client.upload(input_local_path, input_remote_part_path)
        await self.file_system_client.move(input_remote_part_path, input_remote_path)

        # select job by name or create a new one
        job_id = await self.pbs_pro_client.queue_select(PBS_JOB_NAME)

        if job_id:
            try:
                wall_times = await self.pbs_pro_client.queue_status_wall_times(job_id)
                wall_time, wall_time_used = wall_times

                if wall_time_used is None:
                    raise ValueError('Wall time used can not be None because job is running')

                wall_time_left = wall_time - wall_time_used

            except Exception as e:
                logger.error(f'Failed to get wall time because job {job_id} terminated: {e}')
                wall_time_left = None

            if not wall_time_left or wall_time_left < WALL_TIME_THRESHOLD:
                resources = self.pbs_pro_resource_list_loader_service.load(model, use_case='tei')
                job_id = await self.pbs_pro_client.queue_submit(
                    REMOTE_ROOT_PATH,
                    PBS_JOB_NAME,
                    num_nodes=resources.num_nodes,
                    num_cpus=resources.num_cpus,
                    num_gpus=resources.num_gpus,
                    mem=resources.mem,
                    wall_time=resources.wall_time,
                    depend_job_id=job_id,
                    queue=HPCQueue.GPU,
                )

        else:
            resources = self.pbs_pro_resource_list_loader_service.load(model, use_case='tei')
            job_id = await self.pbs_pro_client.queue_submit(
                REMOTE_ROOT_PATH,
                PBS_JOB_NAME,
                num_nodes=resources.num_nodes,
                num_cpus=resources.num_cpus,
                num_gpus=resources.num_gpus,
                mem=resources.mem,
                wall_time=resources.wall_time,
            )

        job = await self.pbs_pro_client.queue_status(job_id)
        logger.info(
            f'Job {job_id} obtained for batch request {batch_request.id} with state {job.state}'
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
        await self.file_system_client.move(batch_job_remote_part_path, batch_job_remote_path)

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

            case PBSProJobState.RUNNING | PBSProJobState.FINISHED | PBSProJobState.EXITED:
                pass

        status_tracker_remote_path = REMOTE_ROOT_PATH / f'status_tracker_{batch_id}.json'
        status_tracker_exists = await self.file_system_client.test(status_tracker_remote_path)

        if not status_tracker_exists:
            logger.warning(
                f'Status tracker {status_tracker_remote_path} is not created yet, '
                f'waiting for {STATUS_TRACKER_DELAY}s'
            )
            await sleep(STATUS_TRACKER_DELAY)

        status_tracker_json = await self.file_system_client.concatenate(status_tracker_remote_path)
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
        output_local_path = LOCAL_ROOT_PATH / '.tmp' / f'output_{batch_request_id}.jsonl'
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
        failed_request_ids = [failed_request.request.id for failed_request in failed_requests]
        finished_request_ids = [response_list.request_id for response_list in response_lists]
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
