from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    EMRequest,
    EMResponse,
)


class BaseBasicEM(ABC):
    @abstractmethod
    async def embed(
        self,
        request: EMRequest,
        *,
        max_time: float,
        max_num_retries: int,
    ) -> EMResponse:
        pass
