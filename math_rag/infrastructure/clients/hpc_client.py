from math_rag.infrastructure.mappings.hpcs import (
    HPCCPUStatisticsMapping,
    HPCGPUStatisticsMapping,
    HPCQueueLiveMapping,
)
from math_rag.infrastructure.models.hpcs import (
    HPCCPUStatistics,
    HPCGPUStatistics,
    HPCQueueLive,
)

from .ssh_client import SSHClient


class HPCClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_live(self) -> HPCQueueLive:
        stdout, stderr = await self.run(
            "qlive | awk 'NR>=5 {print $1, $2, $3, $4, $5}'"
        )

        return HPCQueueLiveMapping.to_source(stdout)

    async def cpu_statistics(self) -> HPCCPUStatistics:
        stdout, stderr = await self.run(
            "jobstat | awk 'NR==3 {print $1, $2, $3, $4, $5, $6, $7, $8}'"
        )

        return HPCCPUStatisticsMapping.to_source(stdout)

    async def gpu_statistics(self) -> HPCGPUStatistics:
        stdout, stderr = await self.run(
            """gpustat | awk 'NR==3 {print $1"_"$2"_"$3"_"$4"_"$5}'"""
        )

        return HPCGPUStatisticsMapping.to_source(stdout)
