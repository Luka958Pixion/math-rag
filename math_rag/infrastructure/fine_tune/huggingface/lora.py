import json

from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from uuid import UUID

from math_rag.infrastructure.clients import (
    ApptainerClient,
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.enums.inference.huggingface import BatchJobStatus
from math_rag.infrastructure.inference.partials import PartialBatchEM
from math_rag.infrastructure.services import FineTuneSettingsLoaderService
from math_rag.infrastructure.utils import (
    FileHasherUtil,
    FileReaderUtil,
    FileStreamWriterUtil,
    FileWriterUtil,
)
from math_rag.infrastructure.validators.inference.huggingface import (
    HuggingFaceModelNameValidator,
)


PBS_JOB_NAME = 'lora'
LOCAL_ROOT_PATH = Path(__file__).parents[4]
REMOTE_ROOT_PATH = Path('lora_default_root')

# must be greater than WALL_TIME_THRESHOLD in lora.py
WALL_TIME_THRESHOLD = timedelta(minutes=35)

logger = getLogger(__name__)


class LoRA:
    def __init__(
        self,
        file_system_client: FileSystemClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_client: ApptainerClient,
        lora_settings_loader_service: FineTuneSettingsLoaderService,
    ):
        self.file_system_client = file_system_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client
        self.apptainer_client = apptainer_client
        self.lora_settings_loader_service = lora_settings_loader_service

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

    def train(self):
        pass
