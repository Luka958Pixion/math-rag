from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset
from math_rag.core.types import ArxivCategoryType


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(
        self,
        dataset: MathExpressionDataset,
        *,
        categories: list[ArxivCategoryType],
        category_limit: int,
    ):
        pass
