from logging import getLogger
from pathlib import Path

import docker

from math_rag.infrastructure.clients import (
    FileSystemClient,
    PBSProClient,
    SFTPClient,
)
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
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
        job_id = await self.pbs_pro_client.queue_select(PBS_JOB_NAME)

        if not job_id:
            return

        job = await self.pbs_pro_client.queue_status(job_id)

        if job.state not in (PBSProJobState.FINISHED, PBSProJobState.EXITED):
            return

        snapshot_json_name = f'snapshot_{job_id}.json'
        snapshot_json_local_path = LOCAL_ROOT_PATH / '.tmp' / snapshot_json_name
        snapshot_json_remote_path = REMOTE_ROOT_PATH / snapshot_json_name

        if not await self.file_system_client.test(snapshot_json_remote_path):
            return

        await self.sftp_client.download(
            snapshot_json_remote_path, snapshot_json_local_path
        )

        snapshot_json = await FileReaderUtil.read_json(snapshot_json_local_path)
        snapshot_response = PrometheusSnapshotResponse.model_validate(snapshot_json)

        if snapshot_response.status == PrometheusSnapshotStatus.ERROR:
            logger.error(
                'Snapshot failed: '
                f'error_type={snapshot_response.error_type}, '
                f'error={snapshot_response.error}'
            )

            return

        snapshot_name = snapshot_response.data.name

        snapshot_remote_path = (
            REMOTE_ROOT_PATH / 'data' / 'snapshots' / snapshot_name
        )  # TODO
        snapshot_local_path = (
            LOCAL_ROOT_PATH / '.tmp' / 'prometheus' / 'snapshots' / snapshot_name
        )  # TODO

        snapshot_archive_remote_path = REMOTE_ROOT_PATH / f'snapshot_{0}.tar.gz'  # TODO
        snapshot_archive_local_path = (
            LOCAL_ROOT_PATH / '.tmp' / 'prometheus' / 'snapshots' / snapshot_name
        )  # TODO

        await self.file_system_client.archive(
            snapshot_remote_path, snapshot_archive_remote_path
        )
        await self.sftp_client.download(
            snapshot_archive_remote_path, snapshot_archive_local_path
        )
        TarFileExtractorUtil.extract_tar_gz_to_path(snapshot_local_path)

        snapshot_id = ...

        client = docker.from_env()
        container = client.containers.get(PROMETHEUS_CONTAINER_NAME)
        container.restart()
