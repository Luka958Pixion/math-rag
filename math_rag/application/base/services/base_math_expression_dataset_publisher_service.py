from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDataset


class BaseMathExpressionDatasetPublisherService(ABC):
    @abstractmethod
    async def publish(self, math_expression_dataset: MathExpressionDataset):
        pass
