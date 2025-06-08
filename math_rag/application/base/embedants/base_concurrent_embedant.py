from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class BaseConcurrentEmbedant(ABC, Generic[EmbedantInputType, EmbedantOutputType]):
    @abstractmethod
    async def concurrent_embed(
        self,
        inputs: list[EmbedantInputType],
    ) -> list[EmbedantOutputType]:
        pass
