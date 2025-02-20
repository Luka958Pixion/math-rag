from abc import ABC, abstractmethod


class GraphRepository(ABC):
    @abstractmethod
    async def create_todo(self, name: str) -> bool:
        pass
