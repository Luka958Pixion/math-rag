from abc import ABC, abstractmethod


class BaseMathExpressionDatasetPublisherService(ABC):
    @abstractmethod
    async def publish(self):
        pass
