from abc import ABC, abstractmethod


class GraphBaseSeeder(ABC):
    @abstractmethod
    async def seed(self, name: str):
        pass
