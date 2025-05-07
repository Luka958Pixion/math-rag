import shlex

from pathlib import Path
from typing import Iterable, overload

from .ssh_client import SSHClient


class FileSystemClient:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    async def test(self, file_path: Path) -> bool:
        stdout = await self.ssh_client.run(
            f'test -f {file_path} && echo "true" || echo "false"'
        )

        return stdout == 'true'

    @overload
    async def remove(self, file_path: Path):
        pass

    @overload
    async def remove(self, file_path: Iterable[Path]):
        pass

    async def remove(self, file_path: Path | Iterable[Path]):
        if isinstance(file_path, Path):
            cmd = f'rm -f {file_path}'

        elif isinstance(file_path, Iterable):
            if not all(isinstance(p, Path) for p in file_path):
                raise TypeError()

            paths = ' '.join(str(p) for p in file_path)
            cmd = f'rm -f {paths}'

        else:
            raise TypeError()

        await self.ssh_client.run(cmd)

    async def make_directory(self, dir_path: Path):
        await self.ssh_client.run(f'mkdir -p {dir_path}')

    async def concatenate(self, file_path: Path) -> str:
        return await self.ssh_client.run(f'cat {file_path}')

    async def move(self, source: Path, target: Path):
        await self.ssh_client.run(f'mv {source} {target}')

    async def echo(self, file_path: Path, content: str):
        if file_path.suffix == '.json':
            content = shlex.quote(content)

        await self.ssh_client.run(f'echo {content} > {file_path}')

    async def hash(self, file_path: Path, hash_function_name: str) -> str:
        return await self.ssh_client.run(
            f"{hash_function_name} {file_path} | awk '{{print $1}}'"
        )

    async def archive(self, source: Path, target: Path):
        await self.ssh_client.run(f'tar -cvf {source} {target}')
