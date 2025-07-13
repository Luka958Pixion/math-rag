from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar


T = TypeVar('T')
U = TypeVar('U')


class BaseGraphRepository(ABC, Generic[T, U]):
    @abstractmethod
    async def insert_one_node(self, item: T):
        pass

    @abstractmethod
    async def insert_many_nodes(self, items: list[T]):
        pass

    @abstractmethod
    async def find_one_node(self, *, filter: dict[str, Any]) -> T | None:
        pass

    @abstractmethod
    async def find_many_nodes(self, *, filter: dict[str, Any]) -> list[T]:
        pass

    @abstractmethod
    async def update_one_node(self, *, filter: dict[str, Any], update: dict[str, Any]):
        pass

    @abstractmethod
    async def insert_one_rel(self, rel: U, *, rel_to_cls: type | None):
        pass

    @abstractmethod
    async def insert_many_rels(self, rels: list[U], *, rel_to_cls: type | None):
        pass

    @abstractmethod
    async def find_many_rels(self, *, filter: dict[str, Any]) -> list[U]:
        pass

    @abstractmethod
    async def clear(self):
        pass
