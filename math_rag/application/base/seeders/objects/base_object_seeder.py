from abc import ABC, abstractmethod


class BaseObjectSeeder(ABC):
    @abstractmethod
    async def seed(self, reset: bool):
        pass
