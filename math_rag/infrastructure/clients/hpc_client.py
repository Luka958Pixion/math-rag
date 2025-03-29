from math_rag.infrastructure.mappings.hpcs import HPCQueueLiveMapping
from math_rag.infrastructure.models.hpcs import HPCQueueLive

from .ssh_client import SSHClient


class HPCClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_live(self) -> HPCQueueLive:
        stdout, stderr = await self.run(
            "qlive | awk 'NR>=5 {print $1, $2, $3, $4, $5}'"
        )

        return HPCQueueLiveMapping.to_source(stdout)
