from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseDatasetRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import DatasetBuildContext
from math_rag.core.models import Dataset
from math_rag.web.requests import DatasetCreateRequest
from math_rag.web.responses import DatasetCreateResponse


BUILD_INDEX_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)
router = APIRouter()


@router.post('/index/create', response_model=DatasetCreateResponse)
@inject
async def create_index(
    dataset_create_request: DatasetCreateRequest = Body(
        ..., description='Parameters for the new index'
    ),
    dataset_repository: BaseDatasetRepository = Depends(
        Provide[ApplicationContainer.index_repository]
    ),
    dataset_build_context: DatasetBuildContext = Depends(
        Provide[ApplicationContainer.index_build_context]
    ),
):
    dataset = Dataset(
        build_from_index_id=dataset_create_request.build_from_index_id,
        build_from_stage=dataset_create_request.build_from_stage,
    )
    await dataset_repository.insert_one(dataset)

    # notify immediately
    async with dataset_build_context.condition:
        dataset_build_context.condition.notify()

    return DatasetCreateResponse(
        id=dataset.id,
        timestamp=dataset.timestamp,
        build_stage=dataset.build_stage,
        build_status=dataset.build_status,
        build_from_index_id=dataset.build_from_index_id,
        build_from_stage=dataset.build_from_stage,
    )
