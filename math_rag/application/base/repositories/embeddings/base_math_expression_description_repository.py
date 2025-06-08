from abc import abstractmethod
from uuid import UUID

from math_rag.core.models import MathExpressionDescription

from .base_embedding_repository import BaseEmbeddingRepository


class BaseMathExpressionDescriptionRepository(BaseEmbeddingRepository[MathExpressionDescription]):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> MathExpressionDescription:
        pass
