import json

from pathlib import Path
from typing import Any, AsyncGenerator

import aiofiles


class FileReaderUtil:
    @staticmethod
    def read(source: Path | bytes) -> str:
        for encoding in ('utf-8', 'latin1', 'cp1252'):
            try:
                if isinstance(source, Path):
                    with open(source, 'r', encoding=encoding) as file:
                        return file.read()

                elif isinstance(source, bytes):
                    return source.decode(encoding)

            except UnicodeDecodeError:
                continue

    @staticmethod
    async def read_json(source: Path) -> dict[str, Any] | list[Any]:
        async with aiofiles.open(source, mode='r', encoding='utf-8') as source_file:
            content = await source_file.read()

            return json.loads(content)

    @staticmethod
    async def read_jsonl(source: Path) -> AsyncGenerator[dict[str, Any], None]:
        async with aiofiles.open(source, mode='r', encoding='utf-8') as source_file:
            async for line in source_file:
                stripped_line = line.strip()

                if stripped_line:
                    yield json.loads(stripped_line)
