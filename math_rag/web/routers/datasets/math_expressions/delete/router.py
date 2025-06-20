from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from math_rag.application.base.repositories.documents import BaseMathExpressionDatasetRepository
from math_rag.application.base.services import BaseDatasetPublisherService
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import MathExpressionDataset


logger = getLogger(__name__)
router = APIRouter()


@router.delete('/datasets/math-expressions', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_math_expression_datasets(
    repository: BaseMathExpressionDatasetRepository = Depends(
        Provide[ApplicationContainer.math_expression_dataset_repository]
    ),
    service: BaseDatasetPublisherService = Depends(
        Provide[ApplicationContainer.dataset_publisher_service]
    ),
):
    dataset_name = MathExpressionDataset.__name__.lower()
    service.unpublish(dataset_name)
    logger.info(f'Unpublished dataset {dataset_name}')

    deleted_count = await repository.clear()
    logger.info(f'Deleted {deleted_count} {dataset_name}(s)')
