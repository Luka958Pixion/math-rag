from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionDatasetPublisherService(ABC):
    @abstractmethod
    async def publish(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        pass
