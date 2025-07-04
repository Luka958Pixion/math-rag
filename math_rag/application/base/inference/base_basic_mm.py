from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    MMRequest,
    MMResult,
)


class BaseBasicMM(ABC):
    @abstractmethod
    async def moderate(
        self,
        request: MMRequest,
        *,
        max_time: float,
        max_num_retries: int,
    ) -> MMResult:
        pass
