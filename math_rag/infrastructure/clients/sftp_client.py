from contextlib import AsyncExitStack
from pathlib import Path
from typing import AsyncGenerator, overload

from asyncssh import ConnectionLost, DisconnectError
from backoff import constant, on_exception

from math_rag.infrastructure.utils import (
    FileStreamerUtil,
    FileStreamReaderUtil,
    FileStreamWriterUtil,
)

from .ssh_client import SSHClient


class SFTPClient:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    @on_exception(constant, (DisconnectError, ConnectionLost), interval=0)
    async def upload(
        self,
        source: Path,
        target: Path,
    ):
        target_str = str(target)

        async with AsyncExitStack() as stack:
            conn = await stack.enter_async_context(self.ssh_client.connect(retry=False))
            sftp = await stack.enter_async_context(conn.start_sftp_client())

            offset = 0

            if sftp.exists(target):
                attrs = await sftp.stat(target_str)
                offset = attrs.size

            target_file = await stack.enter_async_context(
                sftp.open(target_str, 'ab' if offset > 0 else 'wb')
            )
            source_stream = FileStreamerUtil.stream(source, offset)
            await FileStreamWriterUtil.write(source_stream, target_file)

            # with source.open('rb') as f:
            #     f.seek(offset)
            #     while True:
            #         chunk = f.read(32768)
            #         if not chunk:
            #             break
            #         await file.write(chunk)

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
                await FileStreamWriterUtil.write_sftp(file, target)

                return

            return FileStreamReaderUtil.read_sftp(file)
