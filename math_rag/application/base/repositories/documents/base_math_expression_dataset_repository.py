from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import MathExpressionDatasetBuildStage
from math_rag.core.models import MathExpressionDataset

from .base_document_repository import BaseDocumentRepository
from .partials import BaseTaskTrackerRepository


class BaseMathExpressionDatasetRepository(
    BaseDocumentRepository[MathExpressionDataset], BaseTaskTrackerRepository[MathExpressionDataset]
):
    @abstractmethod
    async def update_build_stage(
        self, id: UUID, build_stage: MathExpressionDatasetBuildStage
    ) -> MathExpressionDataset:
        pass
