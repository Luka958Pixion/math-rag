from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequestConcurrent,
    LLMResponseConcurrentBundle,
)
from math_rag.application.types.inference import LLMResponseType


class BaseConcurrentLLM(ABC):
    @abstractmethod
    async def concurrent_generate(
        self,
        request_concurrent: LLMRequestConcurrent[LLMResponseType],
        *,
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_attempts: int,
    ) -> LLMResponseConcurrentBundle[LLMResponseType]:
        pass
