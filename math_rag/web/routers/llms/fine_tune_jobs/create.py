from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import IndexBuildContext
from math_rag.core.models import Index
from math_rag.web.requests import LLMFineTuneJobCreateRequest
from math_rag.web.responses import LLMFineTuneJobCreateResponse


BUILD_INDEX_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)
router = APIRouter()


# TODO
# TODO add to api
@router.post('/llms/fine-tune-jobs', response_model=LLMFineTuneJobCreateResponse)
@inject
async def create_llm_fine_tune_job(
    request: LLMFineTuneJobCreateRequest = Body(...),
    index_repository: BaseIndexRepository = Depends(Provide[ApplicationContainer.index_repository]),
    index_build_context: IndexBuildContext = Depends(
        Provide[ApplicationContainer.index_build_context]
    ),
):
    index = Index(
        build_from_index_id=request.build_from_index_id,
        build_from_stage=request.build_from_stage,
    )
    await index_repository.insert_one(index)

    async with index_build_context.condition:
        index_build_context.condition.notify()

    return LLMFineTuneJobCreateResponse(...)
