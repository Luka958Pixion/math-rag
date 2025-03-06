from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from math_rag.application.models import LLMMessage, LLMParams, LLMResponse


T = TypeVar('T', bound=BaseModel)


class BaseLLM(ABC):
    @abstractmethod
    async def generate_text(
        self, messages: list[LLMMessage], params: LLMParams
    ) -> list[LLMResponse[str]]:
        pass

    @abstractmethod
    async def generate_json(
        self,
        messages: list[LLMMessage],
        params: LLMParams,
        response_model_type: type[T],
    ) -> list[LLMResponse[T]]:
        pass
