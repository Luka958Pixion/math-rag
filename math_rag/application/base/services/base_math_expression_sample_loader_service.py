from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset


class BaseMathExpressionSampleLoaderService(ABC):
    @abstractmethod
    async def load(self, dataset: MathExpressionDataset):
        pass
