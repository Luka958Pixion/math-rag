from logging import getLogger
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from math_rag.application.base.repositories.documents import BaseTaskRepository
from math_rag.application.containers import ApplicationContainer

from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.post('/tasks/{id}', response_model=Response)
@inject
async def read_task(
    id: UUID,
    repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    task = await repository.find_one(filter=dict(id=id))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return Response(task=task)
