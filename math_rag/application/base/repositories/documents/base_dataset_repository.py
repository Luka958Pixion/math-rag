from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import DatasetBuildStage, DatasetBuildStatus
from math_rag.core.models import Dataset

from .base_document_repository import BaseDocumentRepository


class BaseDatasetRepository(BaseDocumentRepository[Dataset]):
    @abstractmethod
    async def update_build_stage(self, id: UUID, build_stage: DatasetBuildStage) -> Dataset:
        pass

    @abstractmethod
    async def update_build_status(
        self, index_id: UUID, build_status: DatasetBuildStatus
    ) -> Dataset:
        pass

    @abstractmethod
    async def find_first_pending(self) -> Dataset | None:
        pass
