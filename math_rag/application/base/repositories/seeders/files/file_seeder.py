from abc import ABC, abstractmethod


class FileBaseSeeder(ABC):
    @abstractmethod
    async def seed(self, name: str):
        pass
