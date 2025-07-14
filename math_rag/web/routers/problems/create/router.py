from logging import getLogger
from pathlib import Path

import aiofiles
import magic

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from math_rag.application.base.clients import BaseLatexConverterClient
from math_rag.application.base.repositories.documents import BaseMathProblemRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathProblem

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
UPLOADS_DIR_PATH = Path(__file__).parents[3] / '.tmp' / 'uploads'
CHUNK_SIZE = 1024 * 1024

logger = getLogger(__name__)
router = APIRouter()


async def validate_file(file: UploadFile):
    # read header
    if file.content_type not in CONTENT_TYPES:
        raise HTTPException(status_code=400, detail='File must be PNG or PDF')

    # read body (double check)
    header = await file.read(1024)
    await file.seek(0)
    actual_content_type = magic.from_buffer(header, mime=True)

    if actual_content_type not in CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f'Invalid file type: {actual_content_type}')


async def write_file(file: UploadFile, dir: Path) -> Path:
    path = dir / file.filename

    async with aiofiles.open(path, 'wb') as out_file:
        while True:
            chunk = await file.read(CHUNK_SIZE)

            if not chunk:
                break

            await out_file.write(chunk)

    await file.close()

    return path


@router.post('/problems', response_model=Response)
@inject
async def create_problem(
    file: UploadFile = File(...),
    mathpix_client: BaseLatexConverterClient = Depends(
        Provide[ApplicationContainer.latex_converter_client]
    ),
    repository: BaseMathProblemRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_repository]
    ),
):
    await validate_file(file)
    path = await write_file(file, UPLOADS_DIR_PATH)

    if path.suffix == '.pdf':
        tex_zip_bytes = mathpix_client.convert_pdf(file_path=path)

    else:
        text = mathpix_client.convert_image(file_path=path)

    math_problem = MathProblem(
        latex=...,
        katex=...,
        is_inline=...,
    )
    await repository.insert_one(math_problem)

    # TODO mock UploadFile in notebook and test there!

    return Response(...)
