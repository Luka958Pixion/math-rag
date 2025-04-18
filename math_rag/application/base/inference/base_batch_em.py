from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchResult,
)


class BaseBatchEM(ABC):
    @abstractmethod
    async def batch_generate(
        self,
        batch_request: EMBatchRequest,
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> EMBatchResult:
        pass

    @abstractmethod
    async def batch_generate_init(
        self,
        batch_request: EMBatchRequest,
    ) -> str:
        pass

    @abstractmethod
    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> EMBatchResult | None:
        pass
