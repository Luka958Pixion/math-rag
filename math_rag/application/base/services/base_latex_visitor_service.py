from abc import ABC, abstractmethod
from typing import Callable

from pylatexenc.latexwalker import LatexNode


class BaseLatexVisitorService(ABC):
    @abstractmethod
    def visit(
        self,
        nodes: list[LatexNode],
        callbacks: dict[type[LatexNode], Callable[[LatexNode], None]],
    ):
        pass
