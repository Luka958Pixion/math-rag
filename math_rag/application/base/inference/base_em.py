from abc import ABC, abstractmethod


class BaseEM(ABC):
    @abstractmethod
    async def embed_text(self, text: str, model: str) -> list[float]:
        pass

    @abstractmethod
    async def embed_texts(self, texts: list[str], model: str) -> list[list[float]]:
        pass
