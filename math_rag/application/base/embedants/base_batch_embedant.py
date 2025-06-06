from abc import ABC, abstractmethod
from typing import Generic
from uuid import UUID

from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class BaseBatchEmbedant(ABC, Generic[EmbedantInputType]):
    @abstractmethod
    async def batch_assist(
        self, inputs: list[EmbedantInputType], *, use_scheduler: bool
    ) -> list[EmbedantOutputType]:
        pass

    @abstractmethod
    async def batch_assist_init(self, inputs: list[EmbedantInputType]) -> str:
        pass

    @abstractmethod
    async def batch_assist_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> list[EmbedantOutputType] | None:
        pass
