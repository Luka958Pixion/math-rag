from contextlib import AsyncExitStack
from pathlib import Path
from typing import AsyncGenerator, overload

from math_rag.infrastructure.utils import FileStreamerUtil

from .ssh_client import SSHClient


class SFTPClient:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    async def upload(
        self,
        source: Path | AsyncGenerator[bytes, None],
        target: Path,
    ):
        if isinstance(source, Path):
            source = FileStreamerUtil.read_file_stream(source)

        async with AsyncExitStack() as stack:
            conn = await stack.enter_async_context(self.ssh_client.connect())
            sftp = await stack.enter_async_context(conn.start_sftp_client())
            file = await stack.enter_async_context(sftp.open(str(target), 'wb'))

            async for chunk in source:
                await file.write(chunk)

    @overload
    async def download(self, source: Path, target: None) -> AsyncGenerator[bytes, None]:
        pass

    @overload
    async def download(self, source: Path, target: Path) -> None:
        pass

    async def download(
        self,
        source: Path,
        target: Path | None,
    ) -> AsyncGenerator[bytes, None] | None:
        async with AsyncExitStack() as stack:
            conn = await stack.enter_async_context(self.ssh_client.connect())
            sftp = await stack.enter_async_context(conn.start_sftp_client())
            file = await stack.enter_async_context(sftp.open(str(source), 'rb'))

            if target:
                await FileStreamerUtil.write_sftp_file_stream(file, target)

                return

            return FileStreamerUtil.read_sftp_file_stream(file)
