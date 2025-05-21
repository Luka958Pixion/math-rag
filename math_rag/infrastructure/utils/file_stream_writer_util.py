from collections.abc import AsyncGenerator
from pathlib import Path

from aiofiles import open
from asyncssh import SFTPClientFile

from math_rag.infrastructure.constants.utils import CHUNK_SIZE


class FileStreamWriterUtil:
    @staticmethod
    async def write(source: AsyncGenerator[bytes, None], target: Path | SFTPClientFile):
        if isinstance(target, Path):
            async with open(target, 'wb') as target_file:
                async for chunk in source:
                    await target_file.write(chunk)

        elif isinstance(target, SFTPClientFile):
            async for chunk in source:
                await target.write(chunk)

    @staticmethod
    async def write_sftp(source: SFTPClientFile, target: Path):
        async with open(target, 'wb') as target_file:
            while True:
                chunk = await source.read(CHUNK_SIZE)

                if not chunk:
                    break

                await target_file.write(chunk)
