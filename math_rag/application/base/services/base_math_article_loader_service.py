from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset, MathExpressionIndex
from math_rag.core.types import ArxivCategoryType


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load_for_dataset(
        self,
        dataset: MathExpressionDataset,
        *,
        categories: list[ArxivCategoryType],
        category_limit: int,
    ):
        pass

    @abstractmethod
    async def load_for_index(self, index: MathExpressionIndex):
        pass
