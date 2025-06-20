from logging import getLogger
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetTestResultRepository,
)
from math_rag.application.containers import ApplicationContainer

from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.get('/results/tests/datasets/math-expressions', response_model=Response)
@inject
async def read_math_expression_dataset_test_result(
    math_expression_dataset_test_id: UUID = Query(...),
    result_repository: BaseMathExpressionDatasetTestResultRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_test_result_repository]
    ),
):
    result = await result_repository.find_one(
        filter=dict(math_expression_dataset_test_id=math_expression_dataset_test_id)
    )

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return Response(math_expression_dataset_test_result=result)
