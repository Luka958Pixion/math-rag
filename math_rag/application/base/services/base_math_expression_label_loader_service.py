from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionLabelLoaderService(ABC):
    @abstractmethod
    async def load(self, index_id: UUID):
        pass
