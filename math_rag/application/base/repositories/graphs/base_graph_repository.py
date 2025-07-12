from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


T = TypeVar('T')
U = TypeVar('U')


class BaseGraphRepository(ABC, Generic[T, U]):
    @abstractmethod
    async def insert_one_node(self, item: T) -> None:
        pass

    @abstractmethod
    async def insert_many_nodes(self, items: list[T]) -> None:
        pass

    @abstractmethod
    async def find_one_node(self, *, filter: dict[str, Any]) -> T | None:
        pass

    @abstractmethod
    async def find_many_nodes(self, *, filter: dict[str, Any]) -> list[T]:
        pass

    @abstractmethod
    async def update_one_node(
        self,
        *,
        filter: dict[str, Any],
        update: dict[str, Any],
    ) -> None:
        pass

    @abstractmethod
    async def insert_one_rel(self, rel: U) -> None:
        pass

    @abstractmethod
    async def insert_many_rels(self, rels: list[U]) -> None:
        pass

    @abstractmethod
    async def find_many_rels(self, *, anchor_filter: dict[str, Any], rel_attr: str) -> list[U]:
        pass
