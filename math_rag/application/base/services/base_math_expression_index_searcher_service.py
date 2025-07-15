from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionIndexSearcherService(ABC):
    @abstractmethod
    async def search(
        self,
        index_id: UUID,
        query: str,
        *,
        query_limit: int,
        limit: int,
    ) -> list[tuple[UUID, UUID, UUID]]:
        pass
