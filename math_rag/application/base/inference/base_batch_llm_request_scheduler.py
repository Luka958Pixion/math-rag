from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchRequestSchedule,
)
from math_rag.application.types.inference import LLMResponseType


class BaseBatchLLMRequestScheduler(ABC):
    @abstractmethod
    def schedule(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        *,
        max_tokens_per_day: float,
        max_input_file_size: int,
    ) -> LLMBatchRequestSchedule[LLMResponseType]:
        pass
