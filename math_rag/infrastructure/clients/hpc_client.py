from math_rag.infrastructure.enums.hpcs import HPCQueue
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

from .ssh_client import SSHClient


class HPCClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_live(self) -> HPCQueueLive:
        stdout, _ = await self.run("qlive | awk 'NR>=5 {print $1, $2, $3, $4, $5}'")

        return HPCQueueLiveMapping.to_source(stdout)

    async def job_statistics(self, queue: HPCQueue) -> HPCJobStatistics | None:
        stdout, _ = await self.run(
            "jobstat -u  | awk 'NR>=3 {print $1, $2, $3, $4, $5, $6, $7, $8}'"
        )

        if stdout == 'No jobs meet the search limits':
            return None

        return HPCJobStatisticsMapping.to_source(stdout)

    async def gpu_statistics(self) -> HPCGPUStatistics | None:
        stdout, _ = await self.run(
            """gpustat | awk 'NR>=3 {print $1"_"$2"_"$3"_"$4"_"$5}'"""
        )

        if stdout.startswith('No running jobs'):
            return None

        return HPCGPUStatisticsMapping.to_source(stdout)

    async def job_temporary_size(self) -> HPCJobTemporarySize:
        stdout, _ = await self.run('job_tmp_size')

        return HPCJobTemporarySizeMapping.to_source(stdout)
