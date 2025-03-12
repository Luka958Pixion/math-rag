from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequest,
    LLMResponseBundle,
)
from math_rag.application.types.inference import LLMResponseType


class BaseLLM(ABC):
    @abstractmethod
    async def generate(
        self,
        request: LLMRequest[LLMResponseType],
        *,
        max_time: float,
        max_num_retries: int,
    ) -> LLMResponseBundle[LLMResponseType]:
        pass
