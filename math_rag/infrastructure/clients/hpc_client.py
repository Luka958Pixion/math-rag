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
        fields = ', '.join(f'${i}' for i in range(1, 5 + 1)).strip()
        stdout = await self.run(f"qlive | awk 'NR>=5 {{print {fields}}}'")

        return HPCQueueLiveMapping.to_source(stdout)

    async def job_statistics(self) -> HPCJobStatistics | None:
        fields = ', '.join(f'${i}' for i in range(1, 8 + 1)).strip()
        stdout = await self.run(
            f"jobstat -u {self.user} | awk 'NR>=4 {{print {fields}}}'"
        )

        if stdout == 'No jobs meet the search limits':
            return None

        return HPCJobStatisticsMapping.to_source(stdout)

    async def gpu_statistics(self) -> HPCGPUStatistics | None:
        fields = '"_"'.join(f'${i}' for i in range(1, 5 + 1)).strip()
        stdout = await self.run(f"gpustat | awk 'NR>=3 {{print {fields}}}'")

        if stdout == f'No running jobs for {self.user}':
            return None

        return HPCGPUStatisticsMapping.to_source(stdout)

    async def job_temporary_size(self) -> HPCJobTemporarySize:
        stdout = await self.run('job_tmp_size')

        return HPCJobTemporarySizeMapping.to_source(stdout)
