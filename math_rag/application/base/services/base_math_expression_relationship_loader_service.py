from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionIndex


class BaseMathExpressionRelationshipLoaderService(ABC):
    @abstractmethod
    async def load_for_index(self, index: MathExpressionIndex):
        pass
