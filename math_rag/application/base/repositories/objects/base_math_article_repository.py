from abc import abstractmethod
from uuid import UUID

from math_rag.core.models import MathArticle

from .base_object_repository import BaseObjectRepository


class BaseMathArticleRepository(BaseObjectRepository[MathArticle]):
    @abstractmethod
    async def find_by_id(self, id: UUID) -> MathArticle | None:
        pass

    @abstractmethod
    async def find_many_by_index_id(self, id: UUID) -> list[MathArticle]:
        pass

    @abstractmethod
    async def find_many_by_math_expression_dataset_id(self, id: UUID) -> list[MathArticle]:
        pass
