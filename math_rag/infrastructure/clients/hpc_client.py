from hashlib import sha256
from pathlib import Path

from math_rag.infrastructure.mappings.hpc import (
    HPCGPUStatisticsMapping,
    HPCJobStatisticsMapping,
    HPCJobTemporarySizeMapping,
    HPCQueueLiveMapping,
)
from math_rag.infrastructure.models.hpc import (
    HPCGPUStatistics,
    HPCJobStatistics,
    HPCJobTemporarySize,
    HPCQueueLive,
)
from math_rag.infrastructure.utils import AwkCmdBuilderUtil

from .ssh_client import SSHClient


class HPCClient:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    async def queue_live(self) -> HPCQueueLive:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=5, col_numbers=range(1, 5 + 1), operator='>='
        )
        stdout = await self.ssh_client.run(f'qlive | {awk_cmd}')

        return HPCQueueLiveMapping.to_source(stdout)

    async def job_statistics(self) -> HPCJobStatistics | None:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=4, col_numbers=range(1, 8 + 1), operator='>='
        )
        stdout = await self.ssh_client.run(f'jobstat -u {self.user} | {awk_cmd}')

        if stdout == 'No jobs meet the search limits':
            return None

        return HPCJobStatisticsMapping.to_source(stdout)

    async def gpu_statistics(self) -> HPCGPUStatistics | None:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=3, col_numbers=range(1, 5 + 1), operator='>=', separator='"_"'
        )
        stdout = await self.ssh_client.run(f'gpustat | {awk_cmd}')

        if stdout == f'No running jobs for {self.user}':
            return None

        return HPCGPUStatisticsMapping.to_source(stdout)

    async def job_temporary_size(self) -> HPCJobTemporarySize:
        stdout = await self.ssh_client.run('job_tmp_size')

        return HPCJobTemporarySizeMapping.to_source(stdout)

    async def has_file_path(self, file_path: Path) -> bool:
        stdout = await self.ssh_client.run(
            f'test -f {file_path} && echo "true" || echo "false"'
        )

        return stdout == 'true'

    async def has_file_changed(
        self, local_file_path: Path, remote_file_path: Path
    ) -> bool:
        with open(local_file_path, 'rb') as local_file:
            local_file_bytes = local_file.read()

        local_file_hash = sha256(local_file_bytes).hexdigest()
        remote_file_hash = await self.ssh_client.run(
            f"sha256sum {remote_file_path} | awk '{{print $1}}'"
        )

        return local_file_hash != remote_file_hash

    async def remove_file(self, file_path: Path):
        await self.ssh_client.run(f'rm -f {file_path}')

    async def remove_files(self, file_paths: list[Path]):
        paths = ' '.join(str(path) for path in file_paths)
        await self.ssh_client.run(f'rm -f {paths}')

    async def make_directory(self, dir_path: Path):
        await self.ssh_client.run(f'mkdir -p {dir_path}')

    async def concatenate(self, file_path: Path) -> str:
        await self.ssh_client.run(f'cat {file_path}')

    async def move(self, source: Path, target: Path):
        await self.ssh_client.run(f'mv {source} {target}')
