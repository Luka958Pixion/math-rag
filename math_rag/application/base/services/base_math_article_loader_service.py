from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.enums.arxiv import BaseArxivCategory


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(self, index_id: UUID, category: BaseArxivCategory, limit: int):
        pass
