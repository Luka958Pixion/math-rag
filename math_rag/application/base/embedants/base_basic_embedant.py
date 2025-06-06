from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class BaseBasicEmbedant(ABC, Generic[EmbedantInputType]):
    @abstractmethod
    async def embed(self, input: EmbedantInputType) -> EmbedantOutputType | None:
        pass
