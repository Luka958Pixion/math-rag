from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import TaskStatus
from math_rag.core.models import Task

from .base_document_repository import BaseDocumentRepository


class BaseTaskRepository(BaseDocumentRepository[Task]):
    @abstractmethod
    async def find_first_pending(self, task_model_name: str) -> Task | None:
        pass

    @abstractmethod
    async def update_task_status(self, id: UUID, task_status: TaskStatus) -> Task:
        pass
