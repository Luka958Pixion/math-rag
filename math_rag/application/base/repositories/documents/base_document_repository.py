from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID


T = TypeVar('T')


class BaseDocumentRepository(ABC, Generic[T]):
    @abstractmethod
    async def insert_one(self, item: T):
        pass

    @abstractmethod
    async def insert_many(self, items: list[T]):
        pass

    @abstractmethod
    async def batch_insert_many(self, items: list[T], *, batch_size: int):
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> T | None:
        pass

    @abstractmethod
    async def find_many(self) -> list[T]:
        pass

    @abstractmethod
    async def clear(self):
        pass

    @abstractmethod
    async def backup(self):
        pass

    @abstractmethod
    async def restore(self):
        pass
