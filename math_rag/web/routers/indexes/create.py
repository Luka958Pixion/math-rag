from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import IndexBuildContext
from math_rag.core.models import Index
from math_rag.web.requests.indexes import IndexCreateRequest
from math_rag.web.responses.indexes import IndexCreateResponse


logger = getLogger(__name__)
router = APIRouter()


@router.post('/indexes', response_model=IndexCreateResponse)
@inject
async def create_index(
    request: IndexCreateRequest = Body(...),
    repository: BaseIndexRepository = Depends(Provide[ApplicationContainer.index_repository]),
    context: IndexBuildContext = Depends(Provide[ApplicationContainer.index_build_context]),
):
    index = Index()
    await repository.insert_one(index)

    async with context.condition:
        context.condition.notify()

    return IndexCreateResponse(
        id=index.id,
        timestamp=index.timestamp,
        build_stage=index.build_stage,
        build_status=index.build_status,
    )
