from logging import getLogger
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetTestResultRepository,
)
from math_rag.application.containers import ApplicationContainer


logger = getLogger(__name__)
router = APIRouter()


@router.delete(
    '/results/tests/datasets/math-expressions/{id}', status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_math_expression_dataset_test_result(
    id: UUID,
    result_repository: BaseMathExpressionDatasetTestResultRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_test_result_repository]
    ),
):
    await result_repository.delete_one(filter=dict(id=id))
