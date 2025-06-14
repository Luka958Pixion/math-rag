from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
)

from .base_latex_node_visitor import BaseLatexNodeVisitor


class LatexMathNodeHelper(BaseLatexNodeVisitor):
    def __init__(self):
        super().__init__()

        self._math_nodes: list[LatexMathNode] = []

    @property
    def math_nodes(self) -> list[LatexMathNode]:
        return self._math_nodes

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
