from logging import getLogger
from pathlib import Path

import docker

from math_rag.infrastructure.clients import (
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.hpc.prometheus import PrometheusSnapshotStatus
from math_rag.infrastructure.models.hpc.prometheus import PrometheusSnapshotResponse
from math_rag.infrastructure.utils import FileReaderUtil, TarFileExtractorUtil


PBS_JOB_NAME = 'tgi'
LOCAL_ROOT_PATH = Path(__file__).parents[3]
REMOTE_ROOT_PATH = Path('tgi_default_root')
PROMETHEUS_CONTAINER_NAME = 'prometheus'


logger = getLogger(__name__)


class PrometheusSnapshotLoaderService:
    def __init__(
        self,
        file_system_client: FileSystemClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
    ):
        self.file_system_client = file_system_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client

    async def load(self):
        # try to get a snapshot json file
        json_remote_path_pattern = REMOTE_ROOT_PATH / 'snapshot_*.json'
        json_remote_path = await self.file_system_client.find(json_remote_path_pattern)

        if not json_remote_path:
            return

        json_local_path = LOCAL_ROOT_PATH / '.tmp' / json_remote_path.name

        if not await self.file_system_client.test(json_remote_path):
            return

        await self.sftp_client.download(json_remote_path, json_local_path)

        snapshot_json = await FileReaderUtil.read_json(json_local_path)
        snapshot_response = PrometheusSnapshotResponse.model_validate(snapshot_json)

        if snapshot_response.status == PrometheusSnapshotStatus.ERROR:
            logger.error(
                'Snapshot failed: '
                f'error_type={snapshot_response.error_type}, '
                f'error={snapshot_response.error}'
            )

            return

        # get an actual snapshot
        snapshot_name = snapshot_response.data.name

        remote_path = REMOTE_ROOT_PATH / 'data' / 'snapshots' / snapshot_name
        local_path = LOCAL_ROOT_PATH / '.tmp' / 'prometheus' / 'snapshots'
        archive_remote_path = REMOTE_ROOT_PATH / f'snapshot_{snapshot_name}.tar'
        archive_local_path = (
            LOCAL_ROOT_PATH
            / '.tmp'
            / 'prometheus'
            / 'snapshots'
            / archive_remote_path.name
        )

        await self.file_system_client.archive(
            remote_path, archive_remote_path, include_root=False
        )
        await self.sftp_client.download(archive_remote_path, archive_local_path)
        TarFileExtractorUtil.extract_tar_gz_to_path(archive_local_path, local_path)

        # cleanup
        json_local_path.unlink()
        archive_local_path.unlink()
        await self.file_system_client.remove([json_remote_path, archive_remote_path])

        # restart prometheus
        client = docker.from_env()
        container = client.containers.get(PROMETHEUS_CONTAINER_NAME)
        container.restart()
