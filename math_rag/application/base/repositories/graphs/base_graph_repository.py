from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar('T')


class BaseGraphRepository(ABC, Generic[T]):
    @abstractmethod
    async def create_node(self):
        pass
