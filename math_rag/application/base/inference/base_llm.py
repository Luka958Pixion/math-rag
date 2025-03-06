from abc import ABC, abstractmethod

from math_rag.application.models import LLMRequest, LLMResponse
from math_rag.application.types import LLMResponseType


class BaseLLM(ABC):
    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> list[LLMResponse[str]]:
        pass

    @abstractmethod
    async def generate_json(
        self, request: LLMRequest
    ) -> list[LLMResponse[LLMResponseType]]:
        pass
