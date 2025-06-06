from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchRequestSchedule,
    EMBatchResult,
)


class BaseBatchEMRequestManagedScheduler(ABC):
    @abstractmethod
    def schedule(
        self,
        batch_request: EMBatchRequest,
    ) -> EMBatchRequestSchedule:
        pass

    @abstractmethod
    async def execute(
        self,
        schedule: EMBatchRequestSchedule,
    ) -> AsyncGenerator[EMBatchResult, None]:
        yield
