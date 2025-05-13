from abc import ABC, abstractmethod

from pylatexenc.latexwalker import LatexMathNode

from math_rag.core.models import MathArticle


class BaseMathArticleParserService(ABC):
    @abstractmethod
    def parse(self, math_article: MathArticle) -> list[LatexMathNode]:
        pass
