import mimetypes

from pathlib import Path
from uuid import uuid4

import aiofiles
import magic


CHUNK_SIZE = 1024 * 1024


class MagicBytesWriterUtil:
    @staticmethod
    async def write(data: bytes, dir_path: Path, *, allowed_content_types: list[str]) -> Path:
        # validate
        header = data[:1024]
        mime_type = magic.from_buffer(header, mime=True)

        if mime_type not in allowed_content_types:
            raise ValueError(f'Invalid mime type: {mime_type}')

        # write
        dir_path.mkdir(parents=True, exist_ok=True)
        extension = mimetypes.guess_extension(mime_type) or str()
        id = uuid4()
        path = dir_path / f'{id.hex}{extension}'

        async with aiofiles.open(path, 'wb') as out_file:
            start = 0
            end = CHUNK_SIZE

            while start < len(data):
                chunk = data[start:end]
                await out_file.write(chunk)
                start = end
                end += CHUNK_SIZE

        return path
