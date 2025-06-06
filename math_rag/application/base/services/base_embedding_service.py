from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class BaseEmbeddingService(ABC, Generic[T]):
    @abstractmethod
    async def index(self, items: list[T]):
        pass

    @abstractmethod
    async def search(self, query: str, *, limit: int) -> list[T]:
        pass
