import mimetypes

from logging import getLogger
from pathlib import Path
from uuid import uuid4

import aiofiles
import magic

from dependency_injector.wiring import inject
from fastapi import APIRouter, Body, HTTPException

from math_rag.application.utils import TokenEncoderUtil

from .response import Response


CONTENT_TYPES = (
    'image/jpeg',
    'image/jpg',
    'image/jpe',
    'image/png',
    'image/bmp',
    'image/dib',
    'image/jp2',
    'image/webp',
    'image/pbm',
    'image/pgm',
    'image/ppm',
    'image/pxm',
    'image/pnm',
    'image/pfm',
    'image/sr',
    'image/ras',
    'image/tiff',
    'image/tif',
    'image/exr',
    'image/hdr',
    'image/pic',
    'application/pdf',
)

UPLOADS_DIR_PATH = Path(__file__).parents[5] / '.tmp' / 'uploads'
CHUNK_SIZE = 1024 * 1024

logger = getLogger(__name__)
router = APIRouter()


async def validate_file(data: bytes) -> str:
    header = data[:1024]
    mime_type = magic.from_buffer(header, mime=True)
    logger.error('here')
    logger.error(mime_type)

    if mime_type not in CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f'Invalid file type: {mime_type}')

    return mime_type


async def write_file(data: bytes, dir_path: Path, mime_type: str) -> Path:
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


@router.post('/files', response_model=Response)
@inject
async def create_file(
    file: bytes = Body(...),
):
    mime_type = await validate_file(file)
    file_path = await write_file(file, UPLOADS_DIR_PATH, mime_type)
    payload = {'file_path': str(file_path)}
    token = TokenEncoderUtil.encode(payload)

    return Response(token=token)
