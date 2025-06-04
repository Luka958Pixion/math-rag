from typing import Callable, TypeAlias

from pylatexenc.latexwalker import LatexNode


VisitLatexNode: TypeAlias = Callable[[LatexNode], None]
LatexNodeVisitor: TypeAlias = dict[type[LatexNode], VisitLatexNode]
