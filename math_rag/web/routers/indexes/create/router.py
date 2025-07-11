from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionIndexRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathExpressionIndex, Task

from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/indexes', response_model=Response)
@inject
async def create_index(
    index_repository: BaseMathExpressionIndexRepository = Depends(
        Provide[ApplicationContainer.math_expression_index_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    index = MathExpressionIndex()
    task = Task(model_id=index.id, model_name=MathExpressionIndex.__name__)

    await index_repository.insert_one(index)
    await task_repository.insert_one(task)

    return Response(index=index, task=task)
