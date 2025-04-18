from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    EMConcurrentRequest,
    EMConcurrentResult,
)


class BaseConcurrentEM(ABC):
    @abstractmethod
    async def concurrent_embed(
        self,
        concurrent_request: EMConcurrentRequest,
        *,
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_num_retries: int,
    ) -> EMConcurrentResult:
        pass
