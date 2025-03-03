from abc import ABC, abstractmethod

from math_rag.application.models import LLMParams


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, params: LLMParams) -> str:
        pass
