from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequestBatch,
    LLMResponseBatch,
)
from math_rag.application.types.inference import LLMResponseType


class BaseConcurrentLLM(ABC):
    @abstractmethod
    async def concurrent_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
    ) -> LLMResponseBatch[LLMResponseType]:
        pass
