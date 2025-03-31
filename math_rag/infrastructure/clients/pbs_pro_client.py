from pathlib import Path

from math_rag.infrastructure.mappings.hpcs.pbs import (
    PBSProJobAlternateMapping,
    PBSProJobFullMapping,
    PBSProJobMapping,
)
from math_rag.infrastructure.models.hpcs.pbs import (
    PBSProJob,
    PBSProJobAlternate,
    PBSProJobFull,
)
from math_rag.infrastructure.utils import AwkCmdBuilderUtil

from .ssh_client import SSHClient


class PBSProClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_submit(self, pbs_path: Path) -> str:
        return await self.run(f'qsub {pbs_path}')

    async def queue_status(
        self, job_id: str, *, alternate: bool, full: bool
    ) -> PBSProJob | PBSProJobAlternate | PBSProJobFull:
        if alternate:
            awk_cmd = AwkCmdBuilderUtil.build(
                row_number=6,
                col_numbers=range(1, 11 + 1),
            )
            stdout = await self.run(f'qstat -a {job_id} | {awk_cmd}')

            return PBSProJobAlternateMapping.to_source(stdout)

        if full:
            stdout = await self.run(f'qstat -f {job_id}')

            return PBSProJobFullMapping.to_source(stdout)

        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=3,
            col_numbers=range(1, 6 + 1),
        )
        stdout = await self.run(f'qstat {job_id} | {awk_cmd}')

        return PBSProJobMapping.to_source(stdout)

    async def queue_delete(self, job_id: str, *, force: bool):
        await self.run(f'qdel -W force -x {job_id}' if force else f'qdel {job_id}')

    async def queue_hold(self, job_id: str):
        await self.run(f'qhold {job_id}')

    async def queue_release(self, job_id: str):
        await self.run(f'qrls {job_id}')

    async def trace_job(self, job_id: str) -> str:
        return await self.run(f'tracejob {job_id}')
