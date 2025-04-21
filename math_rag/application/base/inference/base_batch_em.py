from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchResult,
)


class BaseBatchEM(ABC):
    @abstractmethod
    async def batch_embed(
        self,
        batch_request: EMBatchRequest,
        *,
        poll_interval: float,
        max_tokens_per_day: float,
        max_num_retries: int,
    ) -> EMBatchResult:
        pass

    @abstractmethod
    async def batch_embed_init(
        self,
        batch_request: EMBatchRequest,
        *,
        max_tokens_per_day: float,
    ) -> str:
        pass

    @abstractmethod
    async def batch_embed_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> EMBatchResult | None:
        pass
