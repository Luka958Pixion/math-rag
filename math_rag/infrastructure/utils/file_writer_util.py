from pathlib import Path

from aiofiles import open


class FileWriterUtil:
    @staticmethod
    async def write(source: bytes, target: Path):
        async with open(target, 'wb') as target_file:
            await target_file.write(source)
