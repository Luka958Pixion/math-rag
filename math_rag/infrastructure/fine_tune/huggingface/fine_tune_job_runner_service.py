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
from math_rag.infrastructure.enums.hpc import HPCQueue
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.services import (
    FineTuneSettingsLoaderService,
    PBSProResourceListLoaderService,
)
from math_rag.infrastructure.utils import (
    FileHasherUtil,
    FileReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)
from math_rag.infrastructure.validators.inference.huggingface import HuggingFaceModelNameValidator


PBS_JOB_NAME = 'lora'
LOCAL_ROOT_PATH = Path(__file__).parents[4]
REMOTE_ROOT_PATH = Path('lora_default_root')

# must be greater than WALL_TIME_THRESHOLD in lora.py
WALL_TIME_THRESHOLD = timedelta(minutes=35)

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
            lora_path / 'train.py',
            lora_path / 'metrics.py',
            lora_path / 'fine_tune_settings.py',
            lora_path / 'llama_3_1_8b.py',
            LOCAL_ROOT_PATH / '.env.hpc',
        ]

        for local_path in local_paths:
            assert local_path.exists()

        await self.file_system_client.make_directory(REMOTE_ROOT_PATH)

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

    async def run(self, fine_tune_job: FineTuneJob):
        model = f'{fine_tune_job.provider_name}/{fine_tune_job.model_name}'
        HuggingFaceModelNameValidator.validate(model)

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
                resources = self.pbs_pro_resource_list_loader_service.load(model)
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
            resources = self.pbs_pro_resource_list_loader_service.load(model)
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
