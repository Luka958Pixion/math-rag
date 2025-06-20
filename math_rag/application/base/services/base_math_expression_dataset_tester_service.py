from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionDatasetTest, MathExpressionDatasetTestResult


class BaseMathExpressionDatasetTesterService(ABC):
    @abstractmethod
    async def test(self, test: MathExpressionDatasetTest) -> MathExpressionDatasetTestResult:
        pass
