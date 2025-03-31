from pathlib import Path

from math_rag.infrastructure.mappings.hpcs.pbs import (
    PBSProJobAlternateMapping,
    PBSProJobMapping,
)
from math_rag.infrastructure.models.hpcs.pbs import PBSProJob, PBSProJobAlternate

from .ssh_client import SSHClient


class PBSProClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_submit(self, pbs_path: Path) -> str:
        return await self.run(f'qsub {pbs_path}')

    async def queue_status(
        self, job_id: str, *, alternate: bool
    ) -> PBSProJob | PBSProJobAlternate:
        alternate_flag = '-a' if alternate else str()
        stdout = await self.run(
            f"qstat {alternate_flag}{job_id} | awk 'NR>=3 {{print $1, $2, $3, $4, $5, $6}}'"
        )

        return (
            PBSProJobAlternateMapping.to_source(stdout)
            if alternate
            else PBSProJobMapping.to_source(stdout)
        )

    async def queue_delete(self, job_id: str, *, force: bool):
        await self.run(f'qdel -W force -x {job_id}' if force else f'qdel {job_id}')

    async def queue_hold(self, job_id: str):
        await self.run(f'qhold {job_id}')

    async def queue_release(self, job_id: str):
        await self.run(f'qrls {job_id}')

    async def trace_job(self, job_id: str) -> str:
        return await self.run(f'tracejob {job_id}')
