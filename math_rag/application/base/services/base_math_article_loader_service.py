from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.enums.arxiv import BaseArxivCategory


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(
        self, dataset_id: UUID, arxiv_category_type: type[BaseArxivCategory], limit: int
    ):
        pass
