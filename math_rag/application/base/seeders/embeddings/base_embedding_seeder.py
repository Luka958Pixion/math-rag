from abc import ABC, abstractmethod


class BaseEmbeddingSeeder(ABC):
    @abstractmethod
    async def seed(self, name: str):
        pass
