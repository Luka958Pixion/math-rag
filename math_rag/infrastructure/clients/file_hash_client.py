from pathlib import Path

from .ssh_client import SSHClient


class FileHashClient:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    async def hash(self, hash_function_name: str, file_path: Path) -> str:
        return await self.ssh_client.run(
            f"{hash_function_name} {file_path} | awk '{{print $1}}'"
        )
