from abc import ABC, abstractmethod

from math_rag.application.models.inference import MMRequest, MMResult


class BaseBasicManagedMM(ABC):
    @abstractmethod
    async def moderate(self, request: MMRequest) -> MMResult:
        pass
