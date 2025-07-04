from abc import ABC, abstractmethod
from typing import Generic
from uuid import UUID

from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType


class BaseBatchEmbedder(ABC, Generic[EmbedderInputType, EmbedderOutputType]):
    @abstractmethod
    async def batch_embed(
        self, inputs: list[EmbedderInputType], *, use_scheduler: bool
    ) -> list[EmbedderOutputType]:
        pass

    @abstractmethod
    async def batch_embed_init(self, inputs: list[EmbedderInputType]) -> str:
        pass

    @abstractmethod
    async def batch_embed_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> list[EmbedderOutputType] | None:
        pass
