from abc import ABC, abstractmethod

from math_rag.application.models.inference import MMConcurrentRequest, MMConcurrentResult


class BaseConcurrentManagedMM(ABC):
    @abstractmethod
    async def concurrent_moderate(
        self, concurrent_request: MMConcurrentRequest
    ) -> MMConcurrentResult:
        pass
