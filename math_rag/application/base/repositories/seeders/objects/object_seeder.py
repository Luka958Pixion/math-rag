from abc import ABC, abstractmethod


class ObjectBaseSeeder(ABC):
    @abstractmethod
    async def seed(self, name: str):
        pass
