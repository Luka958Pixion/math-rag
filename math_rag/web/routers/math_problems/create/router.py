from logging import getLogger
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException, status

from math_rag.application.base.clients import BaseLatexConverterClient
from math_rag.application.base.repositories.documents import (
    BaseMathProblemRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.application.utils import TokenEncoderUtil
from math_rag.core.models import MathProblem, Task

from .request import Request
from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/math-problems', response_model=Response)
@inject
async def create_math_problem(
    request: Request = Body(...),
    latex_converter_client: BaseLatexConverterClient = Depends(
        Provide[ApplicationContainer.latex_converter_client]
    ),
    problem_repository: BaseMathProblemRepository = Depends(
        Provide[ApplicationContainer.math_problem_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    try:
        payload = TokenEncoderUtil.decode(request.token)
        file_path = Path(payload['file_path'])

    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')

    latex = latex_converter_client.convert_image(file_path=file_path, url=None)

    problem = MathProblem(math_expression_index_id=request.math_expression_index_id, latex=latex)
    task = Task(model_id=problem.id, model_name=MathProblem.__name__)

    await problem_repository.insert_one(problem)
    await task_repository.insert_one(task)

    return Response(problem=problem, task=task)
