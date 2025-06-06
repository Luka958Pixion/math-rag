from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    EMRequest,
    EMResult,
)


class BaseBasicEM(ABC):
    @abstractmethod
    async def embed(
        self,
        request: EMRequest,
        *,
        max_time: float,
        max_num_retries: int,
    ) -> EMResult:
        pass
