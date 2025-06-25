from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import (
    BaseFineTuneJobRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import FineTuneJob, Task

from .request import Request
from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/fine-tune-jobs', response_model=Response)
@inject
async def create_fine_tune_job(
    request: Request = Body(...),
    job_repository: BaseFineTuneJobRepository = Depends(
        Provide[ApplicationContainer.fine_tune_job_repository]
    ),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    job = FineTuneJob(fine_tune_settings=request.fine_tune_settings)
    task = Task(model_id=job.id, model_name=FineTuneJob.__name__)

    await job_repository.insert_one(job)
    await task_repository.insert_one(task)

    return Response(fine_tune_job=job, task=task)
