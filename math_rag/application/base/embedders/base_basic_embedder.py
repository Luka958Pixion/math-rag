from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType


class BaseBasicEmbedder(ABC, Generic[EmbedderInputType, EmbedderOutputType]):
    @abstractmethod
    async def embed(self, input: EmbedderInputType) -> EmbedderOutputType | None:
        pass
