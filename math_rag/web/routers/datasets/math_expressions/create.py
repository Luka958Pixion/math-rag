from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseMathExpressionDatasetRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import DatasetBuildContext
from math_rag.core.models import MathExpressionDataset
from math_rag.web.requests.datasets.math_expressions import MathExpressionDatasetCreateRequest
from math_rag.web.responses.datasets.math_expressions import MathExpressionDatasetCreateResponse


logger = getLogger(__name__)
router = APIRouter()


@router.post('/datasets/math-expressions', response_model=MathExpressionDatasetCreateResponse)
@inject
async def create_math_expression_dataset(
    request: MathExpressionDatasetCreateRequest = Body(...),
    repository: BaseMathExpressionDatasetRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_repository]
    ),
    context: DatasetBuildContext = Depends(Provide[ApplicationContainer.dataset_build_context]),
):
    dataset = MathExpressionDataset(
        build_from_dataset_id=request.build_from_dataset_id,
        build_from_stage=request.build_from_stage,
    )
    await repository.insert_one(dataset)

    async with context.condition:
        context.condition.notify()

    return MathExpressionDatasetCreateResponse(
        id=dataset.id,
        timestamp=dataset.timestamp,
        build_stage=dataset.build_stage,
        build_status=dataset.build_status,
        build_from_dataset_id=dataset.build_from_dataset_id,
        build_from_stage=dataset.build_from_stage,
    )
