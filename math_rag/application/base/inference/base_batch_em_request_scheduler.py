from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchRequestSchedule,
    EMBatchResult,
)


class BaseBatchEMRequestScheduler(ABC):
    @abstractmethod
    def schedule(
        self,
        batch_request: EMBatchRequest,
        *,
        max_tokens_per_day: float,
        max_input_file_size: int,
    ) -> EMBatchRequestSchedule:
        pass

    @abstractmethod
    async def execute(
        self,
        schedule: EMBatchRequestSchedule,
    ) -> AsyncGenerator[EMBatchResult, None]:
        yield
