from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
)

from math_rag.infrastructure.base import BaseLatexNodeVisitor
from math_rag.infrastructure.types.services import LatexNodeVisitor


class LatexMathNodeHelper(BaseLatexNodeVisitor):
    def __init__(self):
        self._math_nodes: list[LatexMathNode] = []
        self._visitor = {
            LatexCharsNode: self.visit_latex_chars_node,
            LatexCommentNode: self.visit_latex_comment_node,
            LatexEnvironmentNode: self.visit_latex_environment_node,
            LatexMacroNode: self.visit_latex_macro_node,
            LatexMathNode: self.visit_latex_math_node,
            LatexSpecialsNode: self.visit_latex_specials_node,
        }

    @property
    def math_nodes(self) -> list[LatexMathNode]:
        return self._math_nodes

    @property
    def visitor(self) -> LatexNodeVisitor:
        return self._visitor

    def visit_latex_chars_node(self, node: LatexCharsNode):
        pass

    def visit_latex_comment_node(self, node: LatexCommentNode):
        pass

    def visit_latex_environment_node(self, node: LatexEnvironmentNode):
        pass

    def visit_latex_macro_node(self, node: LatexMacroNode):
        pass

    def visit_latex_math_node(self, node: LatexMathNode):
        latex = str(node.latex_verbatim())

        if 'tikz' not in latex and len(latex) < 1000:
            self._math_nodes.append(node)

    def visit_latex_specials_node(self, node: LatexSpecialsNode):
        pass
