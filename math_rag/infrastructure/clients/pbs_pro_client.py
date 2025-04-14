from datetime import timedelta
from pathlib import Path

from math_rag.infrastructure.mappings.hpc.pbs import (
    PBSProJobAlternateMapping,
    PBSProJobFullMapping,
    PBSProJobMapping,
)
from math_rag.infrastructure.models.hpc.pbs import (
    PBSProJob,
    PBSProJobAlternate,
    PBSProJobFull,
)
from math_rag.infrastructure.utils import AwkCmdBuilderUtil

from .ssh_client import SSHClient


class PBSProClient:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    async def queue_submit(
        self,
        project_root_path: Path,
        job_name: str,
        env_vars: dict[str, str] | None = None,
        *,
        num_chunks: int,
        num_cpus: int,
        num_gpus: int,
        mem: int,
        walltime: timedelta,
    ) -> str:
        cmd = f'cd {project_root_path} && qsub '

        if env_vars:
            env_vars_str = ','.join(f'{key}={value}' for key, value in env_vars.items())
            cmd += f'-v {env_vars_str} '

        cmd += (
            f'-l '
            f'select={num_chunks}:ncpus={num_cpus}:mem={mem}B:ngpus={num_gpus},'
            f'walltime={walltime} '
            f'-N {job_name} '
            f'{job_name}.sh'
        )

        return await self.ssh_client.run(cmd)

    async def queue_select(self, job_name: str) -> str | None:
        stdout = await self.ssh_client.run(
            f'qselect -u {self.ssh_client.user} -N {job_name}'
        )

        return stdout or None

    async def queue_signal(self, job_id: str):
        await self.ssh_client.run(f'qsig -s USR1 {job_id}')

    async def queue_status(self, job_id: str) -> PBSProJob:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=3,
            col_numbers=range(1, 6 + 1),
        )
        stdout = await self.ssh_client.run(f'qstat -x {job_id} | {awk_cmd}')

        return PBSProJobMapping.to_source(stdout)

    async def queue_status_alternate(self, job_id: str) -> PBSProJobAlternate:
        awk_cmd = AwkCmdBuilderUtil.build(
            row_number=6,
            col_numbers=range(1, 11 + 1),
        )
        stdout = await self.ssh_client.run(f'qstat -a {job_id} | {awk_cmd}')

        return PBSProJobAlternateMapping.to_source(stdout)

    async def queue_status_full(self, job_id: str) -> PBSProJobFull:
        stdout = await self.ssh_client.run(f'qstat -f {job_id}')

        return PBSProJobFullMapping.to_source(stdout)

    async def queue_delete(self, job_id: str, *, force: bool):
        await self.ssh_client.run(
            f'qdel -W force -x {job_id}' if force else f'qdel {job_id}'
        )

    async def queue_hold(self, job_id: str):
        await self.ssh_client.run(f'qhold {job_id}')

    async def queue_release(self, job_id: str):
        await self.ssh_client.run(f'qrls {job_id}')

    async def trace_job(self, job_id: str) -> str:
        return await self.ssh_client.run(f'tracejob {job_id}')
