from abc import ABC, abstractmethod


class BaseGraphSeeder(ABC):
    @abstractmethod
    async def seed(self, reset: bool):
        pass
