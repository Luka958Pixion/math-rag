from abc import ABC, abstractmethod

from pylatexenc.latexwalker import LatexNode


class BaseLatexParserService(ABC):
    @abstractmethod
    def parse(self, latex: str) -> list[LatexNode]:
        pass
