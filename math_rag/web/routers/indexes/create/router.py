from logging import getLogger
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException, status

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionIndexRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.application.utils import TokenEncoderUtil
from math_rag.core.models import MathExpressionIndex, MathExpressionIndexBuildDetails, Task

from .request import Request
from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/indexes', response_model=Response)
@inject
async def create_index(
    request: Request = Body(...),
    index_repository: BaseMathExpressionIndexRepository = Depends(
        Provide[ApplicationContainer.math_expression_index_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    try:
        payload = TokenEncoderUtil.decode(request.token)
        file_path = Path(payload['file_path'])

    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')

    index_build_details = MathExpressionIndexBuildDetails(file_path=file_path)
    index = MathExpressionIndex(build_details=index_build_details)
    task = Task(model_id=index.id, model_name=MathExpressionIndex.__name__)

    await index_repository.insert_one(index)
    await task_repository.insert_one(task)

    return Response(index=index, task=task)
