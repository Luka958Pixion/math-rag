from pathlib import Path
from typing import AsyncGenerator

from aiofiles import open


CHUNK_SIZE = 8192


class BytesStreamerUtil:
    async def stream_bytes(data: bytes) -> AsyncGenerator[bytes, None]:
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i : i + CHUNK_SIZE]

            yield chunk

    @staticmethod
    async def stream_file(path: Path) -> AsyncGenerator[bytes, None]:
        async with open(path, 'rb') as file:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk
