from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar
from uuid import UUID

from math_rag.application.types.repositories.embeddings import GroupCallback


T = TypeVar('T')


class BaseEmbeddingRepository(ABC, Generic[T]):
    @abstractmethod
    async def upsert_one(self, item: T, embedding: list[float]):
        pass

    @abstractmethod
    async def upsert_many(self, items: list[T], embeddings: list[list[float]]):
        pass

    @abstractmethod
    async def find_one(self, id: UUID) -> T | None:
        pass

    @abstractmethod
    async def find_many(self, ids: list[UUID]) -> list[T]:
        pass

    @abstractmethod
    async def search(
        self, embedding: list[float], *, filter: dict[str, Any] | None, limit: int
    ) -> list[T]:
        pass

    @abstractmethod
    async def group(self, callback: GroupCallback) -> list[list[T]]:
        pass

    @abstractmethod
    async def clear(self):
        pass

    @abstractmethod
    async def backup(self) -> Path:
        pass

    @abstractmethod
    async def restore(self, backup_path: Path):
        pass
