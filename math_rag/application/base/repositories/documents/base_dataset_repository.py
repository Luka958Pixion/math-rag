from abc import abstractmethod
from typing import Generic
from uuid import UUID

from math_rag.core.base import BaseDataset
from math_rag.core.enums import DatasetBuildStatus
from math_rag.core.types import DatasetBuildStageType, SampleType

from .base_document_repository import BaseDocumentRepository


class BaseDatasetRepository(
    BaseDocumentRepository[SampleType], Generic[SampleType, DatasetBuildStageType]
):
    @abstractmethod
    async def update_build_stage(
        self, id: UUID, build_stage: DatasetBuildStageType
    ) -> BaseDataset[SampleType, DatasetBuildStageType]:
        pass

    @abstractmethod
    async def update_build_status(
        self, index_id: UUID, build_status: DatasetBuildStatus
    ) -> BaseDataset[SampleType, DatasetBuildStageType]:
        pass

    @abstractmethod
    async def find_first_pending(self) -> BaseDataset[SampleType, DatasetBuildStageType] | None:
        pass
