from abc import ABC, abstractmethod
from typing import Generic
from uuid import UUID

from math_rag.core.enums import TaskStatus
from math_rag.infrastructure.types.repositories.documents import DocumentType


class BaseTaskTrackerRepository(ABC, Generic[DocumentType]):
    @abstractmethod
    async def find_first_pending(self) -> DocumentType | None:
        pass

    @abstractmethod
    async def update_task_status(self, id: UUID, task_status: TaskStatus) -> DocumentType:
        pass
