from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import IndexBuildContext
from math_rag.core.models import Index
from math_rag.web.responses import IndexCreateResponse


BUILD_INDEX_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)
router = APIRouter()


@router.post('/index/create', response_model=IndexCreateResponse)
@inject
async def create_index(
    index_repository: BaseIndexRepository = Depends(
        Provide[ApplicationContainer.index_repository]
    ),
    index_build_context: IndexBuildContext = Depends(
        Provide[ApplicationContainer.index_build_context]
    ),
):
    index = Index()
    await index_repository.insert_one(index)

    # notify immediately
    async with index_build_context.condition:
        index_build_context.condition.notify()

    return IndexCreateResponse(**index.model_dump())
