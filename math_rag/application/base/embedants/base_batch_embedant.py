from abc import ABC, abstractmethod
from typing import Generic
from uuid import UUID

from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class BaseBatchEmbedant(ABC, Generic[EmbedantInputType, EmbedantOutputType]):
    @abstractmethod
    async def batch_embed(
        self, inputs: list[EmbedantInputType], *, use_scheduler: bool
    ) -> list[EmbedantOutputType]:
        pass

    @abstractmethod
    async def batch_embed_init(self, inputs: list[EmbedantInputType]) -> str:
        pass

    @abstractmethod
    async def batch_embed_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> list[EmbedantOutputType] | None:
        pass
