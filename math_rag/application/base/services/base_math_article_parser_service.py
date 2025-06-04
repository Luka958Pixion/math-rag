from abc import ABC, abstractmethod

from math_rag.core.models import LatexMathNode, MathArticle


class BaseMathArticleParserService(ABC):
    @abstractmethod
    def parse_for_dataset(self, math_article: MathArticle) -> list[LatexMathNode]:
        pass

    @abstractmethod
    def parse_for_index(
        self, math_article: MathArticle
    ) -> tuple[list[LatexMathNode], list[int], str]:
        pass
