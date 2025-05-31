from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import MathExpressionDatasetBuildStage, MathExpressionDatasetBuildStatus
from math_rag.core.models import MathExpressionDataset

from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionDatasetRepository(
    BaseDocumentRepository[MathExpressionDataset],
):
    @abstractmethod
    async def update_build_stage(
        self, id: UUID, build_stage: MathExpressionDatasetBuildStage
    ) -> MathExpressionDataset:
        pass

    @abstractmethod
    async def update_build_status(
        self, id: UUID, build_status: MathExpressionDatasetBuildStatus
    ) -> MathExpressionDataset:
        pass

    @abstractmethod
    async def find_first_pending(self) -> MathExpressionDataset | None:
        pass
