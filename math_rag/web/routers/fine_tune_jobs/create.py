from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import (
    BaseFineTuneJobRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import FineTuneJob, Task
from math_rag.shared.utils import TypeUtil
from math_rag.web.requests.fine_tune_jobs import FineTuneJobCreateRequest
from math_rag.web.responses.fine_tune_jobs import FineTuneJobCreateResponse


logger = getLogger(__name__)
router = APIRouter()


@router.post('/fine-tune-jobs', response_model=FineTuneJobCreateResponse)
@inject
async def create_fine_tune_job(
    request: FineTuneJobCreateRequest = Body(...),
    job_repository: BaseFineTuneJobRepository = Depends(
        Provide[ApplicationContainer.fine_tune_job_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    job = FineTuneJob(provider_name=request.provider_name, model_name=request.model_name)
    task = Task(model_id=job.id, model_type=TypeUtil.to_fqn(FineTuneJob))

    await job_repository.insert_one(job)
    await task_repository.insert_one(task)

    return FineTuneJobCreateResponse(fine_tune_job=job, task=task)
