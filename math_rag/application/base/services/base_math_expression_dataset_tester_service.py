from abc import ABC, abstractmethod


class BaseMathExpressionDatasetTesterService(ABC):
    @abstractmethod
    async def test(self):
        pass
