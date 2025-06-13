from abc import ABC, abstractmethod

from arxiv import Result

from math_rag.core.enums.arxiv import BaseArxivCategory


class BaseArxivClient(ABC):
    @abstractmethod
    def search(self, category: BaseArxivCategory, limit: int) -> list[Result]:
        pass

    @abstractmethod
    async def get_pdf(self, arxiv_id: str) -> tuple[str, bytes] | None:
        pass

    @abstractmethod
    async def get_src(self, arxiv_id: str) -> tuple[str, bytes] | None:
        pass
