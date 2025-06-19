from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseMathExpressionDatasetRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import DatasetTestContext
from math_rag.core.models import MathExpressionDataset
from math_rag.web.requests.tests.datasets.math_expressions import (
    MathExpressionDatasetTestCreateRequest,
)
from math_rag.web.responses.tests.datasets.math_expressions import (
    MathExpressionDatasetTestCreateResponse,
)


logger = getLogger(__name__)
router = APIRouter()


# TODO
# TODO DI
@router.post(
    '/tests/datasets/math-expressions', response_model=MathExpressionDatasetTestCreateResponse
)
@inject
async def create_math_expression_dataset(
    request: MathExpressionDatasetTestCreateRequest = Body(...),
    repository: BaseMathExpressionDatasetRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_repository]
    ),
    context: DatasetTestContext = Depends(Provide[ApplicationContainer.dataset_test_context]),
):
    dataset = MathExpressionDataset(
        build_from_id=request.build_from_id,
        build_from_stage=request.build_from_stage,
        build_priority=request.build_priority,
        build_details=request.build_details,
    )
    await repository.insert_one(dataset)

    async with context.condition:
        context.condition.notify()

    return MathExpressionDatasetTestCreateResponse(labels=...)
