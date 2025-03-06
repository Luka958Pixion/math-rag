from abc import ABC, abstractmethod

from math_rag.application.models import LLMRequest, LLMResponse
from math_rag.application.types import LLMResponseType


class BaseLLM(ABC):
    @abstractmethod
    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> list[LLMResponse[LLMResponseType]]:
        pass
