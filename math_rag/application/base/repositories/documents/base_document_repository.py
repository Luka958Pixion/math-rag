from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Generic, TypeVar
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
    async def find_one(self, *, filter: dict[str, Any] | None = None) -> T | None:
        pass

    @abstractmethod
    async def find_many(self, *, filter: dict[str, Any] | None = None) -> list[T]:
        pass

    @abstractmethod
    async def batch_find_many(
        self, *, batch_size: int, filter: dict[str, Any] | None = None
    ) -> AsyncGenerator[list[T], None]:
        yield

    @abstractmethod
    async def clear(self):
        pass

    @abstractmethod
    async def backup(self):
        pass

    @abstractmethod
    async def restore(self):
        pass
