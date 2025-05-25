from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import IndexBuildContext
from math_rag.core.models import Index
from math_rag.web.requests import IndexCreateRequest
from math_rag.web.responses import IndexCreateResponse


BUILD_INDEX_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)
router = APIRouter()


@router.post('/index/create', response_model=IndexCreateResponse)
@inject
async def create_index(
    index_create_request: IndexCreateRequest = Body(
        ..., description='Parameters for the new index'
    ),
    index_repository: BaseIndexRepository = Depends(
        Provide[ApplicationContainer.index_repository]
    ),
    index_build_context: IndexBuildContext = Depends(
        Provide[ApplicationContainer.index_build_context]
    ),
):
    index = Index(
        build_from_index_id=index_create_request.build_from_index_id,
        build_from_stage=index_create_request.build_from_stage,
    )
    await index_repository.insert_one(index)

    # notify immediately
    async with index_build_context.condition:
        index_build_context.condition.notify()

    return IndexCreateResponse(
        id=index.id,
        timestamp=index.timestamp,
        build_stage=index.build_stage,
        build_status=index.build_status,
        build_from_index_id=index.build_from_index_id,
        build_from_stage=index.build_from_stage,
    )
