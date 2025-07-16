from logging import getLogger
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.clients import BaseLatexConverterClient
from math_rag.application.containers import ApplicationContainer
from math_rag.application.utils import MagicBytesWriterUtil, TokenEncoderUtil

from .response import Response


UPLOADS_DIR_PATH = Path(__file__).parents[5] / '.tmp' / 'uploads'

logger = getLogger(__name__)
router = APIRouter()


@router.post('/files', response_model=Response)
@inject
async def create_file(
    file: bytes = Body(...),
    latex_converter_client: BaseLatexConverterClient = Depends(
        Provide[ApplicationContainer.latex_converter_client]
    ),
):
    file_path = await MagicBytesWriterUtil.write(
        file, UPLOADS_DIR_PATH, allowed_content_types=latex_converter_client.list_content_types()
    )
    payload = {'file_path': str(file_path)}
    token = TokenEncoderUtil.encode(payload)

    return Response(token=token)
