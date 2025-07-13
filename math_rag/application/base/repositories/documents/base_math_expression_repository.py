from abc import abstractmethod
from uuid import UUID

from math_rag.core.models import MathExpression

from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionRepository(BaseDocumentRepository[MathExpression]):
    @abstractmethod
    async def update_group_id(self, ids: list[UUID], group_id: UUID | None):
        pass
