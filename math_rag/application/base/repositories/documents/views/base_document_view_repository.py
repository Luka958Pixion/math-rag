from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Generic, TypeVar


T = TypeVar('T')


class BaseDocumentViewRepository(ABC, Generic[T]):
    @abstractmethod
    async def find_many(self) -> list[T]:
        pass

    @abstractmethod
    async def batch_find_many(self, *, batch_size: int) -> AsyncGenerator[list[T], None]:
        yield
