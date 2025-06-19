from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseFineTuneJobRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.application.contexts import FineTuneJobRunContext
from math_rag.core.models import FineTuneJob
from math_rag.web.requests.fine_tune_jobs import FineTuneJobCreateRequest
from math_rag.web.responses.fine_tune_jobs import FineTuneJobCreateResponse


logger = getLogger(__name__)
router = APIRouter()


@router.post('/fine-tune-jobs', response_model=FineTuneJobCreateResponse)
@inject
async def create_fine_tune_job(
    request: FineTuneJobCreateRequest = Body(...),
    repository: BaseFineTuneJobRepository = Depends(
        Provide[ApplicationContainer.fine_tune_job_repository]
    ),
    context: FineTuneJobRunContext = Depends(
        Provide[ApplicationContainer.fine_tune_job_run_context]
    ),
):
    fine_tune_job = FineTuneJob(provider_name=request.provider_name, model_name=request.model_name)
    await repository.insert_one(fine_tune_job)

    async with context.condition:
        context.condition.notify()

    return FineTuneJobCreateResponse(
        id=fine_tune_job.id,
        timestamp=fine_tune_job.timestamp,
        status=fine_tune_job.run_status,
        provider_name=fine_tune_job.provider_name,
        model_name=fine_tune_job.model_name,
    )
