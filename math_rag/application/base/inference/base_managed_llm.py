from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequest,
    LLMResult,
)
from math_rag.application.types.inference import LLMResponseType


class BaseManagedLLM(ABC):
    @abstractmethod
    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> LLMResult[LLMResponseType]:
        pass
