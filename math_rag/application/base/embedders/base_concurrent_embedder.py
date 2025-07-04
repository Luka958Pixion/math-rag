from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType


class BaseConcurrentEmbedder(ABC, Generic[EmbedderInputType, EmbedderOutputType]):
    @abstractmethod
    async def concurrent_embed(
        self,
        inputs: list[EmbedderInputType],
    ) -> list[EmbedderOutputType]:
        pass
