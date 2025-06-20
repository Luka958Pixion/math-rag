from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from math_rag.application.base.repositories.documents import BaseTaskRepository
from math_rag.application.containers import ApplicationContainer

from .request import Request
from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/tasks', response_model=Response)
@inject
async def read_task(
    request: Request = Body(...),
    repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    task = await repository.find_one(filter=dict(id=request.task_id))

    return Response(task=task)
