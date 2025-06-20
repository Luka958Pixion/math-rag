from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetTestRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathExpressionDatasetTest, Task

from .request import Request
from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/tests/datasets/math-expressions', response_model=Response)
@inject
async def create_math_expression_dataset_test(
    request: Request = Body(...),
    test_repository: BaseMathExpressionDatasetTestRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_test_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    test = MathExpressionDatasetTest(
        math_expression_dataset_id=request.math_expression_dataset_id,
        math_expression_dataset_split_name=request.math_expression_dataset_split_name,
        inference_provider=request.inference_provider,
        model_provider=request.model_provider,
        model=request.model,
    )
    task = Task(model_id=test.id, model_name=MathExpressionDatasetTest.__name__)

    await test_repository.insert_one(test)
    await task_repository.insert_one(task)

    return Response(math_expression_dataset_test=test, task=task)
