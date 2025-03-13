from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMConcurrentRequest,
    LLMConcurrentResult,
)
from math_rag.application.types.inference import LLMResponseType


class BaseConcurrentLLM(ABC):
    @abstractmethod
    async def concurrent_generate(
        self,
        concurrent_request: LLMConcurrentRequest[LLMResponseType],
        *,
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_num_retries: int,
    ) -> LLMConcurrentResult[LLMResponseType]:
        pass
