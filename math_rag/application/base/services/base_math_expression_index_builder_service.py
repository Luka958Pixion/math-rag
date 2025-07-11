from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionIndex


class BaseMathExpressionIndexBuilderService(ABC):
    @abstractmethod
    async def build(self, index: MathExpressionIndex):
        pass
