from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathExpressionDataset, Task

from .request import Request
from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/datasets/math-expressions', response_model=Response)
@inject
async def create_math_expression_dataset(
    request: Request = Body(...),
    dataset_repository: BaseMathExpressionDatasetRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    dataset = MathExpressionDataset(
        build_from_id=request.build_from_id,
        build_from_stage=request.build_from_stage,
        build_priority=request.build_priority,
        build_details=request.build_details,
    )
    task = Task(model_id=dataset.id, model_name=MathExpressionDataset.__name__)

    await dataset_repository.insert_one(dataset)
    await task_repository.insert_one(task)

    return Response(math_expression_dataset=dataset, task=task)
