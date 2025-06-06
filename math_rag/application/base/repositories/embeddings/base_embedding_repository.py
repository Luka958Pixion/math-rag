from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID


T = TypeVar('T')


class BaseEmbeddingRepository(ABC, Generic[T]):
    @abstractmethod
    async def upsert_one(self, item: T, embedding: list[float]):
        pass

    @abstractmethod
    async def upsert_many(self, items: list[T], embeddings: list[list[float]]):
        pass

    @abstractmethod
    async def find_many(self, ids: list[UUID]) -> list[T]:
        pass

    @abstractmethod
    async def search(self, embedding: list[float], *, limit: int) -> list[T]:
        pass
