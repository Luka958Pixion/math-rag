from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import IndexBuildStage
from math_rag.core.models import Index

from .base_document_repository import BaseDocumentRepository
from .partials import BaseTaskTrackerRepository


class BaseIndexRepository(BaseDocumentRepository[Index], BaseTaskTrackerRepository[Index]):
    @abstractmethod
    async def update_build_stage(self, id: UUID, build_stage: IndexBuildStage) -> Index:
        pass
