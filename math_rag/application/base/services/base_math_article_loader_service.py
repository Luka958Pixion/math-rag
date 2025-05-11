from abc import ABC, abstractmethod


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(self):
        pass
