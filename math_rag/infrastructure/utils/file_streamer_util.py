import json

from pathlib import Path
from typing import Any, AsyncGenerator

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

    @staticmethod
    async def read_jsonl_file_stream(
        stream: AsyncGenerator[bytes, None],
    ) -> AsyncGenerator[dict[str, Any], None]:
        buffer: bytes = b''

        async for chunk in stream:
            buffer += chunk

            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)

                if line.strip():
                    yield json.loads(line)

        if buffer.strip():
            yield json.loads(buffer)
