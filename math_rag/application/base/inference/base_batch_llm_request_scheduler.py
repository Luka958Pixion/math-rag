from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchRequestSchedule,
)
from math_rag.application.types.inference import LLMResponseType


class BaseBatchLLMRequestScheduler(ABC):
    @abstractmethod
    async def schedule(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        *,
        max_tokens_per_day: float | None,
        max_input_file_size: int | None,
    ) -> LLMBatchRequestSchedule[LLMResponseType]:
        pass
