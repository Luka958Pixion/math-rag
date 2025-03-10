from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType


class BaseLLM(ABC):
    @abstractmethod
    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> LLMResponseList[LLMResponseType] | None:
        pass
