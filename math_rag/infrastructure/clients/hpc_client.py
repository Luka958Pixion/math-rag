from math_rag.infrastructure.mappings.hpcs import (
    HPCGPUStatisticsMapping,
    HPCJobStatisticsMapping,
    HPCJobTemporarySizeMapping,
    HPCQueueLiveMapping,
)
from math_rag.infrastructure.models.hpcs import (
    HPCGPUStatistics,
    HPCJobStatistics,
    HPCJobTemporarySize,
    HPCQueueLive,
)
from math_rag.infrastructure.utils import AwkCmdBuilderUtil

from .ssh_client import SSHClient


class HPCClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_live(self) -> HPCQueueLive:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=6, col_numbers=range(1, 5 + 1), operator='>='
        )
        stdout = await self.run(f'qlive | {awk_cmd}')

        return HPCQueueLiveMapping.to_source(stdout)

    async def job_statistics(self) -> HPCJobStatistics | None:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=4, col_numbers=range(1, 8 + 1), operator='>='
        )
        stdout = await self.run(f'jobstat -u {self.user} | {awk_cmd}')

        if stdout == 'No jobs meet the search limits':
            return None

        return HPCJobStatisticsMapping.to_source(stdout)

    async def gpu_statistics(self) -> HPCGPUStatistics | None:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=3, col_numbers=range(1, 5 + 1), operator='>=', separator='"_"'
        )
        stdout = await self.run(f'gpustat | {awk_cmd}')

        if stdout == f'No running jobs for {self.user}':
            return None

        return HPCGPUStatisticsMapping.to_source(stdout)

    async def job_temporary_size(self) -> HPCJobTemporarySize:
        stdout = await self.run('job_tmp_size')

        return HPCJobTemporarySizeMapping.to_source(stdout)
