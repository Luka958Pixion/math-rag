from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository, BaseTaskRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.core.models import Index, Task
from math_rag.shared.utils import TypeUtil
from math_rag.web.responses.indexes import IndexCreateResponse


logger = getLogger(__name__)
router = APIRouter()


@router.post('/indexes', response_model=IndexCreateResponse)
@inject
async def create_index(
    index_repository: BaseIndexRepository = Depends(Provide[ApplicationContainer.index_repository]),
    task_repository: BaseTaskRepository = Depends(Provide[ApplicationContainer.task_repository]),
):
    index = Index()
    task = Task(model_id=index.id, model_type=TypeUtil.to_fqn(Index))

    await index_repository.insert_one(index)
    await task_repository.insert_one(task)

    return IndexCreateResponse(index=index, task=task)
