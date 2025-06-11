from logging import getLogger
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, UploadFile

from math_rag.application.base.clients import BaseLatexConverterClient
from math_rag.application.base.repositories.documents import BaseMathProblemRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathProblem
from math_rag.web.requests import ProblemCreateRequest
from math_rag.web.responses import ProblemCreateResponse


UPLOADS_PATH = Path(__file__).parents[3] / '.tmp' / 'uploads'

logger = getLogger(__name__)
router = APIRouter()


@router.post('/problems', response_model=ProblemCreateResponse)
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
    content = await file.read()
    # TODO write

    await file.close()

    math_problem = MathProblem(
        latex=...,
        katex=...,
        is_inline=...,
    )
    await repository.insert_one(math_problem)

    return ProblemCreateResponse(...)
