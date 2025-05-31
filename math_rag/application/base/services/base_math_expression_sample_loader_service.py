from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionSampleLoaderService(ABC):
    @abstractmethod
    async def load(self, dataset_id: UUID, foundation_dataset_id: UUID | None):
        pass
