from abc import ABC, abstractmethod


class BaseEM(ABC):
    @abstractmethod
    async def embed(self, text: str, model: str) -> list[float]:
        pass
