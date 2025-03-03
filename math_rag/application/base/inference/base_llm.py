from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from math_rag.application.models import LLMParams


TBaseLLMResponseModel = TypeVar('T', bound=BaseModel)


class BaseLLM(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, params: LLMParams) -> str:
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        params: LLMParams,
        response_model_type: type[TBaseLLMResponseModel],
    ) -> TBaseLLMResponseModel:
        pass
