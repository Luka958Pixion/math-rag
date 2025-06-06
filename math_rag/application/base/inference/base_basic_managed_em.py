from abc import ABC, abstractmethod

from math_rag.application.models.inference import EMRequest, EMResult


class BaseBasicManagedEM(ABC):
    @abstractmethod
    async def embed(self, request: EMRequest) -> EMResult:
        pass
