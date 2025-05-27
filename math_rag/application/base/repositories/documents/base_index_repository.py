from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import IndexBuildStage, IndexBuildStatus
from math_rag.core.models import Index

from .base_document_repository import BaseDocumentRepository


class BaseIndexRepository(BaseDocumentRepository[Index]):
    @abstractmethod
    async def update_build_stage(self, id: UUID, build_stage: IndexBuildStage) -> Index:
        pass

    @abstractmethod
    async def update_build_status(
        self, index_id: UUID, build_status: IndexBuildStatus
    ) -> Index:
        pass

    @abstractmethod
    async def find_first_pending(self) -> Index | None:
        pass
