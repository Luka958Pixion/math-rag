from abc import ABC, abstractmethod

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
)

from math_rag.infrastructure.types.services import LatexNodeVisitor


class BaseLatexNodeVisitor(ABC):
    def __init__(self):
        self._visitor = {
            LatexCharsNode: self.visit_latex_chars_node,
            LatexCommentNode: self.visit_latex_comment_node,
            LatexEnvironmentNode: self.visit_latex_environment_node,
            LatexMacroNode: self.visit_latex_macro_node,
            LatexMathNode: self.visit_latex_math_node,
            LatexSpecialsNode: self.visit_latex_specials_node,
        }

    @property
    def visitor(self) -> LatexNodeVisitor:
        return self._visitor

    @abstractmethod
    def visit_latex_chars_node(self, node: LatexCharsNode):
        pass

    @abstractmethod
    def visit_latex_comment_node(self, node: LatexCommentNode):
        pass

    @abstractmethod
    def visit_latex_environment_node(self, node: LatexEnvironmentNode):
        pass

    @abstractmethod
    def visit_latex_macro_node(self, node: LatexMacroNode):
        pass

    @abstractmethod
    def visit_latex_math_node(self, node: LatexMathNode):
        pass

    @abstractmethod
    def visit_latex_specials_node(self, node: LatexSpecialsNode):
        pass
