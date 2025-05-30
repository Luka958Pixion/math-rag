from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset


class BaseMathExpressionDatasetBuilderService(ABC):
    @abstractmethod
    async def build(self, dataset: MathExpressionDataset):
        pass
