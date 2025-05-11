from abc import ABC, abstractmethod

from math_rag.application.enums.arxiv import BaseArxivCategory


class BaseMathArticleLoaderService(ABC):
    @abstractmethod
    async def load(self, category: BaseArxivCategory, limit: int):
        pass
