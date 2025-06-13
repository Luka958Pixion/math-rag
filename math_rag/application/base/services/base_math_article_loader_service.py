from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset
from math_rag.core.types.arxiv import ArxivCategoryType


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(
        self,
        dataset: MathExpressionDataset,
        *,
        arxiv_category_type: type[ArxivCategoryType] | None,
        arxiv_category: ArxivCategoryType | None,
        limit: int,
    ):
        pass
