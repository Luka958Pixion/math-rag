from datetime import timedelta
from pathlib import Path

from math_rag.infrastructure.enums.hpc import HPCQueue
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
        num_nodes: int,
        num_cpus: int,
        num_gpus: int,
        mem: int,
        wall_time: timedelta,
        depend_job_id: str | None = None,
        queue: HPCQueue = HPCQueue.GPU,
    ) -> str:
        cmd = f'cd {project_root_path} && qsub '

        if env_vars:
            env_vars_str = ','.join(f'{key}={value}' for key, value in env_vars.items())
            cmd += f'-v {env_vars_str} '

        if depend_job_id:
            cmd += f'-W depend=afterok:{depend_job_id} '

        cmd += (
            f'-q {queue.value} '
            f'-l select={num_nodes}:ncpus={num_cpus}:mem={mem}B:ngpus={num_gpus},'
            f'walltime={wall_time} '
            f'-N {job_name} '
            f'{job_name}.sh'
        )

        return await self.ssh_client.run(cmd)

    async def queue_select(self, job_name: str) -> str | None:
        stdout = await self.ssh_client.run(f'qselect -u {self.ssh_client.user} -N {job_name}')

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

    async def queue_status_wall_times(self, job_id: str) -> tuple[timedelta, timedelta | None]:
        awk_cmd = AwkCmdBuilderUtil.build_wall_times()
        stdout = await self.ssh_client.run(f'qstat -f {job_id} | {awk_cmd}')
        wall_times = stdout.strip().splitlines()

        hours, minutes, seconds = map(int, wall_times[0].split(':'))
        wall_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        if len(wall_times) == 2:
            hours, minutes, seconds = map(int, wall_times[1].split(':'))
            wall_time_used = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        else:
            wall_time_used = None

        return wall_time, wall_time_used

    async def queue_delete(self, job_id: str, *, force: bool):
        await self.ssh_client.run(f'qdel -W force -x {job_id}' if force else f'qdel {job_id}')

    async def queue_hold(self, job_id: str):
        await self.ssh_client.run(f'qhold {job_id}')

    async def queue_release(self, job_id: str):
        await self.ssh_client.run(f'qrls {job_id}')

    async def trace_job(self, job_id: str) -> str:
        return await self.ssh_client.run(f'tracejob {job_id}')
