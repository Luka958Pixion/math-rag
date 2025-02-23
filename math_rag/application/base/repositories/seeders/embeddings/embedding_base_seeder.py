from abc import ABC, abstractmethod


class EmbeddingBaseSeeder(ABC):
    @abstractmethod
    async def seed(self, name: str):
        pass
