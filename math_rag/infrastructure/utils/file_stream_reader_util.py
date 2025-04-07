import json

from typing import Any, AsyncGenerator

from asyncssh import SFTPClientFile

from math_rag.infrastructure.constants.utils import CHUNK_SIZE


class FileStreamReaderUtil:
    @staticmethod
    async def read_sftp(
        source: SFTPClientFile,
    ) -> AsyncGenerator[bytes, None]:
        while True:
            chunk = await source.read(CHUNK_SIZE)

            if not chunk:
                break

            yield chunk

    @staticmethod
    async def read_jsonl(
        source: AsyncGenerator[bytes, None],
    ) -> AsyncGenerator[dict[str, Any], None]:
        buffer: bytes = b''

        async for chunk in source:
            buffer += chunk

            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)

                if line.strip():
                    yield json.loads(line)

        if buffer.strip():
            yield json.loads(buffer)
