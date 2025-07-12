from abc import abstractmethod
from uuid import UUID

from math_rag.core.models import MathExpressionContext

from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionContextRepository(BaseDocumentRepository[MathExpressionContext]):
    @abstractmethod
    async def update_group_id(self, ids: list[UUID], group_id: UUID):
        pass
