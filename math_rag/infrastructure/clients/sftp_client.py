from contextlib import AsyncExitStack
from pathlib import Path

from asyncssh import ConnectionLost, DisconnectError
from backoff import constant, on_exception

from math_rag.infrastructure.utils import (
    FileStreamerUtil,
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
            conn = await stack.enter_async_context(self.ssh_client.connect())
            sftp = await stack.enter_async_context(conn.start_sftp_client())

            offset = 0

            if await sftp.exists(target):
                attrs = await sftp.stat(target_str)
                offset = attrs.size

                if offset is None:
                    raise ValueError()

            target_file = await stack.enter_async_context(
                sftp.open(target_str, 'ab' if offset > 0 else 'wb')
            )
            source_stream = FileStreamerUtil.stream(source, offset)
            await FileStreamWriterUtil.write(source_stream, target_file)

    async def download(
        self,
        source: Path,
        target: Path,
    ):
        async with AsyncExitStack() as stack:
            conn = await stack.enter_async_context(self.ssh_client.connect())
            sftp = await stack.enter_async_context(conn.start_sftp_client())
            source_file = await stack.enter_async_context(sftp.open(str(source), 'rb'))

            await FileStreamWriterUtil.write_sftp(source_file, target)
