from abc import ABC, abstractmethod


class GraphRepository(ABC):
    @abstractmethod
    async def create_node(self, name: str):
        pass
