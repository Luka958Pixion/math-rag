from abc import ABC, abstractmethod


class DocumentBaseSeeder(ABC):
    @abstractmethod
    async def seed(self, name: str):
        pass
