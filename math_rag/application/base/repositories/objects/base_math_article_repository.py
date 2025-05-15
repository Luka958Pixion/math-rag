from abc import ABC, abstractmethod

from math_rag.core.models import MathArticle


class BaseMathArticleRepository(ABC):
    @abstractmethod
    def insert_many(self, items: list[MathArticle]):
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> MathArticle:
        pass

    @abstractmethod
    def list_names(self) -> list[str]:
        pass

    @abstractmethod
    def backup(self):
        pass

    @abstractmethod
    def restore(self):
        pass
