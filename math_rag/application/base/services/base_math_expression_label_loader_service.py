from abc import ABC, abstractmethod

from math_rag.core.models import Index, MathExpressionDataset


class BaseMathExpressionLabelLoaderService(ABC):
    @abstractmethod
    async def load_for_dataset(self, dataset: MathExpressionDataset):
        pass

    @abstractmethod
    async def load_for_index(self, index: Index):
        pass
