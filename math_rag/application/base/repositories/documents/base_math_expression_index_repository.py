from abc import abstractmethod
from uuid import UUID

from math_rag.core.enums import MathExpressionIndexBuildStage
from math_rag.core.models import MathExpressionIndex

from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionIndexRepository(BaseDocumentRepository[MathExpressionIndex]):
    @abstractmethod
    async def update_build_stage(
        self, id: UUID, build_stage: MathExpressionIndexBuildStage
    ) -> MathExpressionIndex:
        pass
