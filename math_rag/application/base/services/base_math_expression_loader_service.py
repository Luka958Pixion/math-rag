from abc import ABC, abstractmethod


class BaseMathExpressionLoaderService(ABC):
    @abstractmethod
    async def load(self):
        pass
