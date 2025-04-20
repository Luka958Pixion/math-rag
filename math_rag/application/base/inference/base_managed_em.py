from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    EMRequest,
    EMResponse,
)


class BaseManagedEM(ABC):
    @abstractmethod
    async def embed(self, request: EMRequest) -> EMResponse:
        pass
