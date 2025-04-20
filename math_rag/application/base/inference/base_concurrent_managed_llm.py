from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMConcurrentRequest,
    LLMConcurrentResult,
)
from math_rag.application.types.inference import LLMResponseType


class BaseConcurrentManagedLLM(ABC):
    @abstractmethod
    async def concurrent_generate(
        self, concurrent_request: LLMConcurrentRequest[LLMResponseType]
    ) -> LLMConcurrentResult[LLMResponseType]:
        pass
