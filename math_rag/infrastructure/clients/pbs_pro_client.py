from pathlib import Path

from .ssh_client import SSHClient


class PBSProClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def queue_submit(self, pbs_path: Path) -> str:
        stdout = await self.run(f'qsub {pbs_path}')

        return stdout

    async def queue_state(self):
        stdout = await self.run(
            f"qstat -u {self.user} | awk 'NR>=3 {{print $1, $2, $3, $4, $5, $6}}'"
        )
        # TODO parse

        return stdout

    async def queue_delete(self, job_id: str, force: bool):
        # qdel
        stdout = await self.run(
            f'qdel -W force -x {job_id}' if force else f'qdel {job_id}'
        )

        return stdout

    async def queue_hold(self, job_id: str):
        # qhold
        stdout = await self.run(f'qhold {job_id}')

        return stdout

    async def queue_release(self, job_id: str):
        # qrls
        stdout = await self.run(f'qrls {job_id}')

        return stdout

    async def trace_job(self, job_id: str):
        # tracejob
        stdout = await self.run(f'tracejob {job_id}')

        return stdout
