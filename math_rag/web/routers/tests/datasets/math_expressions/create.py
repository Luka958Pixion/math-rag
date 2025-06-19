from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathExpressionDatasetTest, Task
from math_rag.web.requests.tests.datasets.math_expressions import (
    MathExpressionDatasetTestCreateRequest,
)
from math_rag.web.responses.tests.datasets.math_expressions import (
    MathExpressionDatasetTestCreateResponse,
)


logger = getLogger(__name__)
router = APIRouter()


@router.post(
    '/tests/datasets/math-expressions', response_model=MathExpressionDatasetTestCreateResponse
)
@inject
async def create_math_expression_dataset_test(
    request: MathExpressionDatasetTestCreateRequest = Body(...),
    test_repository: BaseMathExpressionDatasetRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_repository]
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
    task = Task(model_id=test.id)

    await test_repository.insert_one(test)
    await task_repository.insert_one(task)

    return MathExpressionDatasetTestCreateResponse(math_expression_dataset_test=test, task=task)
