from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import FineTuneJobRunStatus
from math_rag.core.models import FineTuneJob

from .base_document_repository import BaseDocumentRepository


class BaseFineTuneJobRepository(BaseDocumentRepository[FineTuneJob]):
    @abstractmethod
    async def update_build_status(self, id: UUID, run_status: FineTuneJobRunStatus) -> FineTuneJob:
        pass

    @abstractmethod
    async def find_first_pending(self) -> FineTuneJob | None:
        pass
