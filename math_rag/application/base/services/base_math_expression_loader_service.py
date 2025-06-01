from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionLoaderService(ABC):
    @abstractmethod
    async def load(self, index_id: UUID, build_from_dataset_id: UUID | None):
        pass
