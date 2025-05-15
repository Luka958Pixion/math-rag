from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar('T')


class BaseObjectRepository(ABC, Generic[T]):
    @abstractmethod
    def insert_many(self, items: list[T]):
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> T:
        pass

    @abstractmethod
    def list_names(self) -> list[str | None]:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def backup(self):
        pass

    @abstractmethod
    def restore(self):
        pass
