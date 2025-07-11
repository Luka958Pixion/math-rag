from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset, MathExpressionIndex


class BaseMathExpressionLabelLoaderService(ABC):
    @abstractmethod
    async def load_for_dataset(self, dataset: MathExpressionDataset):
        pass

    @abstractmethod
    async def load_for_index(self, index: MathExpressionIndex):
        pass
