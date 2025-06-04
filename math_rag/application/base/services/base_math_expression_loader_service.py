from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionLoaderService(ABC):
    @abstractmethod
    async def load_for_dataset(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        pass

    @abstractmethod
    async def load_for_index(self, index_id: UUID):
        pass
