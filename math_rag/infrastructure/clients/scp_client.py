from contextlib import AsyncExitStack
from pathlib import Path
from typing import AsyncGenerator

from aiofiles import open

from .ssh_client import SSHClient


class SCPClient(SSHClient):
    def __init__(self, host: str, user: str, passphrase: str):
        super().__init__(host, user, passphrase)

    async def upload(
        self,
        source: Path | AsyncGenerator[bytes, None],
        target: Path,
    ):
        if isinstance(source, Path):
            source = self._stream_file(source)

        async with AsyncExitStack() as stack:
            conn = await stack.enter_async_context(self.connect())
            sftp = await stack.enter_async_context(conn.start_sftp_client())
            file = await stack.enter_async_context(sftp.open(str(target), 'wb'))

            async for chunk in source:
                await file.write(chunk)

    async def _stream_file(self, path: Path) -> AsyncGenerator[bytes, None]:
        async with open(path, 'rb') as file:
            while True:
                chunk = await file.read(8192)

                if not chunk:
                    break

                yield chunk

    async def download(
        self,
        source: Path,
        target: Path,
    ):
        async with AsyncExitStack() as stack:
            conn = await stack.enter_async_context(self.connect())
            sftp = await stack.enter_async_context(conn.start_sftp_client())
            file = await stack.enter_async_context(sftp.open(str(source), 'rb'))

            async with open(target, 'wb') as source_file:
                while True:
                    chunk = await file.read(8192)

                    if not chunk:
                        break

                    await source_file.write(chunk)
