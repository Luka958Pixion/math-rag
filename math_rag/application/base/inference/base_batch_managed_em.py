from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchResult,
)


class BaseBatchManagedEM(ABC):
    @abstractmethod
    async def batch_embed(self, batch_request: EMBatchRequest) -> EMBatchResult:
        pass

    @abstractmethod
    async def batch_embed_init(
        self,
        batch_request: EMBatchRequest,
    ) -> str:
        pass

    @abstractmethod
    async def batch_embed_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> EMBatchResult | None:
        pass
