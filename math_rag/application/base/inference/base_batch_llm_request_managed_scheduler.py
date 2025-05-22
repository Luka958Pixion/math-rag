from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchRequestSchedule,
    LLMBatchResult,
)
from math_rag.application.types.inference import LLMResponseType


class BaseBatchLLMRequestManagedScheduler(ABC):
    @abstractmethod
    def schedule(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> LLMBatchRequestSchedule[LLMResponseType]:
        pass

    @abstractmethod
    async def execute(
        self,
        schedule: LLMBatchRequestSchedule[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> AsyncGenerator[LLMBatchResult[LLMResponseType], None]:
        yield
