from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.types.arxiv import ArxivCategoryType


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(
        self,
        dataset_id: UUID,
        *,
        arxiv_category_type: type[ArxivCategoryType] | None,
        arxiv_category: ArxivCategoryType | None,
    ):
        pass
