from abc import ABC, abstractmethod

from math_rag.application.models.inference import MMConcurrentRequest, MMConcurrentResult


class BaseConcurrentMM(ABC):
    @abstractmethod
    async def concurrent_moderate(
        self,
        concurrent_request: MMConcurrentRequest,
        *,
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_num_retries: int,
    ) -> MMConcurrentResult:
        pass
