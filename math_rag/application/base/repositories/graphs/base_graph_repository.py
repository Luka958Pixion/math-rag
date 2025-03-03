from abc import ABC, abstractmethod


class BaseGraphRepository(ABC):
    @abstractmethod
    async def create_node(self, name: str):
        pass

    @abstractmethod
    async def delete_node(self, name: str):
        pass
