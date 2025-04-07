from pathlib import Path
from typing import AsyncGenerator

from aiofiles import open


class FileWriterUtil:
    @staticmethod
    async def write(stream: AsyncGenerator[bytes, None], path: Path):
        async with open(path, 'wb') as file:
            async for chunk in stream:
                await file.write(chunk)
