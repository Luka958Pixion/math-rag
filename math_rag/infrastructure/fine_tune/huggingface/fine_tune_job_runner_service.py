from asyncio import sleep
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from uuid import UUID

from math_rag.application.base.fine_tune import BaseFineTuneJobRunnerService
from math_rag.core.models import FineTuneJob
from math_rag.infrastructure.clients import (
    ApptainerClient,
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.fine_tune.huggingface import HelperJobStatus
from math_rag.infrastructure.enums.hpc import HPCQueue
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.models.fine_tune.huggingface import (
    HelperJob,
    HelperJobStatusTracker,
)
from math_rag.infrastructure.services import (
    FineTuneSettingsLoaderService,
    PBSProResourceListLoaderService,
)
from math_rag.infrastructure.utils import (
    FileHasherUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)
from math_rag.infrastructure.validators.inference.huggingface import HuggingFaceModelNameValidator
from math_rag.shared.utils import YamlWriterUtil


PBS_JOB_NAME = 'lora'
LOCAL_ROOT_PATH = Path(__file__).parents[4]
REMOTE_ROOT_PATH = Path('lora_default_root')

# must be greater than WALL_TIME_THRESHOLD in lora.py
WALL_TIME_THRESHOLD = timedelta(minutes=35)
STATUS_TRACKER_DELAY = 30

logger = getLogger(__name__)


class FineTuneJobRunnerService(BaseFineTuneJobRunnerService):
    def __init__(
        self,
        file_system_client: FileSystemClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_client: ApptainerClient,
        fine_tune_settings_loader_service: FineTuneSettingsLoaderService,
        pbs_pro_resource_list_loader_service: PBSProResourceListLoaderService,
    ):
        self.file_system_client = file_system_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client
        self.apptainer_client = apptainer_client
        self.fine_tune_settings_loader_service = fine_tune_settings_loader_service
        self.pbs_pro_resource_list_loader_service = pbs_pro_resource_list_loader_service

    async def init_resources(self):
        tmp_path = LOCAL_ROOT_PATH / '.tmp'
        hf_path = LOCAL_ROOT_PATH / 'assets/hpc/hf'
        lora_path = hf_path / 'lora'

        # NOTE: order matters
        local_paths = [
            lora_path / 'requirements.txt',
            lora_path / 'lora.def',
            lora_path / 'lora.py',
            lora_path / 'lora.sh',
            lora_path / 'optuna.py',
            lora_path / 'metrics.py',
            lora_path / 'utils.py',
            lora_path / 'fine_tune_settings.py',
            lora_path / 'fine_tune.py',
            lora_path / 'llama_3_1_8b.py',
            LOCAL_ROOT_PATH / '.env.hpc',
        ]

        for local_path in local_paths:
            assert local_path.exists()

        await self.file_system_client.make_directory(REMOTE_ROOT_PATH)
        await self.file_system_client.make_directory(REMOTE_ROOT_PATH / 'home')

        for local_path in local_paths:
            remote_path = REMOTE_ROOT_PATH / local_path.name

            if await self.file_system_client.test(remote_path):
                local_hash = FileHasherUtil.hash(local_path, 'sha256')
                remote_hash = await self.file_system_client.hash(remote_path, 'sha256sum')

                if local_hash != remote_hash:
                    await self.file_system_client.remove(remote_path)

                    logger.info(f'Upload started: {local_path}')

                else:
                    logger.info(f'Upload skipped: {local_path} unchanged')
                    continue

            if local_path.suffix == '.def':
                sif_stream = await self.apptainer_client.build(
                    local_path,
                    lora_path / 'requirements.txt' if local_path.name == 'lora.def' else None,
                )

                sif_local_path = tmp_path / f'{local_path.stem}.sif'
                await FileStreamWriterUtil.write(sif_stream, sif_local_path)

                sif_remote_path = REMOTE_ROOT_PATH / sif_local_path.name

                if await self.file_system_client.test(sif_remote_path):
                    await self.file_system_client.remove(sif_remote_path)

                await self.sftp_client.upload(sif_local_path, sif_remote_path)

            await self.sftp_client.upload(local_path, remote_path)

    async def init(self, fine_tune_job: FineTuneJob) -> str:
        model = f'{fine_tune_job.provider_name}/{fine_tune_job.model_name}'
        HuggingFaceModelNameValidator.validate(model)

        # load settings
        fine_tune_settings = self.fine_tune_settings_loader_service.load(
            fine_tune_job.provider_name, fine_tune_job.model_name
        )

        # write input file
        input_local_path = LOCAL_ROOT_PATH / '.tmp' / f'input_{fine_tune_job.id}.yaml'
        YamlWriterUtil.write(input_local_path, model=fine_tune_settings)

        # upload input file and avoid race-conditions
        input_remote_path = REMOTE_ROOT_PATH / input_local_path.name
        input_remote_part_path = input_remote_path.with_name(input_remote_path.name + '.part')
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
                    raise ValueError('Wall time used can not be None because job is running')

                wall_time_left = wall_time - wall_time_used

            except Exception as e:
                logger.error(f'Failed to get wall time because job {job_id} terminated: {e}')
                wall_time_left = None

            if not wall_time_left or wall_time_left < WALL_TIME_THRESHOLD:
                resources = self.pbs_pro_resource_list_loader_service.load(model, use_case='ft')
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
            resources = self.pbs_pro_resource_list_loader_service.load(model, use_case='ft')
            job_id = await self.pbs_pro_client.queue_submit(
                REMOTE_ROOT_PATH,
                PBS_JOB_NAME,
                num_nodes=resources.num_chunks,
                num_cpus=resources.num_cpus,
                num_gpus=resources.num_gpus,
                mem=resources.mem,
                wall_time=resources.wall_time,
                queue=HPCQueue.GPU,
            )

        job = await self.pbs_pro_client.queue_status(job_id)
        logger.info(
            f'Job {job_id} obtained for fine tune job {fine_tune_job.id} with state {job.state}'
        )

        # create in-memory helper job file
        helper_job = HelperJob(
            fine_tune_job_id=fine_tune_job.id,
            timestamp=int(datetime.now().timestamp()),
        )
        helper_job_json_str = helper_job.model_dump_json()
        helper_job_json_bytes = helper_job_json_str.encode('utf-8')

        # write helper job file
        helper_job_local_path = (
            LOCAL_ROOT_PATH / '.tmp' / f'helper_job_{job_id}_{fine_tune_job.id}.json'
        )
        await FileWriterUtil.write(helper_job_json_bytes, helper_job_local_path)

        # upload helper job file and avoid race-conditions
        helper_job_remote_path = REMOTE_ROOT_PATH / helper_job_local_path.name
        helper_job_remote_part_path = helper_job_remote_path.with_name(
            helper_job_remote_path.name + '.part'
        )
        await self.sftp_client.upload(helper_job_local_path, helper_job_remote_part_path)
        await self.file_system_client.move(helper_job_remote_part_path, helper_job_remote_path)

        return job_id

    async def result(
        self,
        job_id: str,
        fine_tune_job_id: UUID,
    ) -> dict | None:
        job = await self.pbs_pro_client.queue_status(job_id)
        logger.info(f'Job {job_id} state {job.state}')

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

        status_tracker_remote_path = REMOTE_ROOT_PATH / f'status_tracker_{job_id}.json'
        status_tracker_exists = await self.file_system_client.test(status_tracker_remote_path)

        if not status_tracker_exists:
            logger.warning(
                f'Status tracker {status_tracker_remote_path} is not created yet, '
                f'waiting for {STATUS_TRACKER_DELAY}s'
            )
            await sleep(STATUS_TRACKER_DELAY)

        status_tracker_json = await self.file_system_client.concatenate(status_tracker_remote_path)
        status_tracker = HelperJobStatusTracker.model_validate_json(status_tracker_json)

        if fine_tune_job_id not in status_tracker.id_to_status:
            return None

        status = status_tracker.id_to_status[fine_tune_job_id]

        match status:
            case HelperJobStatus.WAITING | HelperJobStatus.RUNNING:
                return None

            case HelperJobStatus.FINISHED | HelperJobStatus.UNFINISHED:
                pass

        input_local_path = LOCAL_ROOT_PATH / '.tmp' / f'input_{fine_tune_job_id}.yaml'
        input_remote_path = REMOTE_ROOT_PATH / input_local_path.name

        await self.file_system_client.remove([input_remote_path])
        input_local_path.unlink()

        # NOTE: we are not sure what to return here at the moment
        return {}

    async def run(self, fine_tune_job: FineTuneJob, *, poll_interval: float) -> dict:
        job_id = await self.init(fine_tune_job)

        while True:
            result = await self.result(job_id, fine_tune_job.id)

            if result is not None:
                return result

            await sleep(poll_interval)
