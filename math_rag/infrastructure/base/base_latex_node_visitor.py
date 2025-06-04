from abc import ABC, abstractmethod

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
)


class BaseLatexNodeVisitor(ABC):
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
