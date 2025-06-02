from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import IndexBuildContext
from math_rag.core.models import FineTuneJob
from math_rag.web.requests import FineTuneJobCreateRequest
from math_rag.web.responses import FineTuneJobCreateResponse


logger = getLogger(__name__)
router = APIRouter()


# TODO
# TODO add to api
@router.post('/fine-tune-jobs', response_model=FineTuneJobCreateResponse)
@inject
async def create_llm_fine_tune_job(
    request: FineTuneJobCreateRequest = Body(...),
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

    return FineTuneJobCreateResponse(...)
