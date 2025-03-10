from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequestConcurrent,
    LLMResponseConcurrent,
)
from math_rag.application.types.inference import LLMResponseType


class BaseConcurrentLLM(ABC):
    @abstractmethod
    async def concurrent_generate(
        self,
        request_batch: LLMRequestConcurrent[LLMResponseType],
    ) -> LLMResponseConcurrent[LLMResponseType]:
        pass
