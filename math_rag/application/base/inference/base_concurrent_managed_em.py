from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    EMConcurrentRequest,
    EMConcurrentResult,
)


class BaseConcurrentManagedEM(ABC):
    @abstractmethod
    async def concurrent_embed(
        self, concurrent_request: EMConcurrentRequest
    ) -> EMConcurrentResult:
        pass
