from pathlib import Path
from typing import AsyncGenerator

from aiofiles import open
from asyncssh import SFTPClientFile


CHUNK_SIZE = 8192


class FileStreamerUtil:
    @staticmethod
    async def read_file_stream(path: Path) -> AsyncGenerator[bytes, None]:
        async with open(path, 'rb') as file:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk

    @staticmethod
    async def read_sftp_file_stream(
        file: SFTPClientFile,
    ) -> AsyncGenerator[bytes, None]:
        while True:
            chunk = await file.read(CHUNK_SIZE)

            if not chunk:
                break

            yield chunk

    @staticmethod
    async def write_sftp_file_stream(source_file: SFTPClientFile, target: Path):
        async with open(target, 'wb') as target_file:
            while True:
                chunk = await source_file.read(CHUNK_SIZE)

                if not chunk:
                    break

                await target_file.write(chunk)
