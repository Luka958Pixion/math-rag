from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar('T')


class BaseEmbeddingRepository(ABC, Generic[T]):
    @abstractmethod
    async def upsert_one(self, item: T):
        pass

    @abstractmethod
    async def upsert_many(self, items: list[T]):
        pass

    @abstractmethod
    async def batch_upsert_many(self, items: list[T], *, batch_size: int):
        pass

    @abstractmethod
    async def search(self, embedding: list[float], top_k: int) -> list[T]:
        pass
