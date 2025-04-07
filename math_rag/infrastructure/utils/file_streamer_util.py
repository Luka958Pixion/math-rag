from pathlib import Path
from typing import AsyncGenerator

from aiofiles import open

from math_rag.infrastructure.constants.utils import CHUNK_SIZE


class FileStreamerUtil:
    @staticmethod
    async def stream(
        source: Path, offset: int | None = None
    ) -> AsyncGenerator[bytes, None]:
        async with open(source, 'rb') as source_file:
            if offset:
                source_file.seek(offset, whence=0)

            while True:
                chunk = await source_file.read(CHUNK_SIZE)

                if not chunk:
                    break

                yield chunk
