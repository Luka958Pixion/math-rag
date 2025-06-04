import re

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


IMAGE_PLACEHOLDER = '[image_placeholder]'
MATH_PLACEHOLDER = '[math_placeholder]'
MATH_PLACEHOLDER_PATTERN = r'\[math_placeholder\]'


class TemplateHelper(BaseLatexNodeVisitor):
    def __init__(self):
        self._strings: list[str] = []
        self._visitor = {
            LatexCharsNode,
            self.visit_latex_chars_node,
            LatexCommentNode,
            self.visit_latex_comment_node,
            LatexEnvironmentNode,
            self.visit_latex_environment_node,
            LatexMacroNode,
            self.visit_latex_macro_node,
            LatexMathNode,
            self.visit_latex_math_node,
            LatexSpecialsNode,
            self.visit_latex_specials_node,
        }

    @property
    def template(self) -> str:
        return str().join(self._strings)

    @property
    def positions(self) -> str:
        return [match.start() for match in re.finditer(MATH_PLACEHOLDER_PATTERN, self.template)]

    @property
    def visitor(self) -> LatexNodeVisitor:
        return self._visitor

    def visit_latex_chars_node(self, node: LatexCharsNode):
        self._strings.append(node.chars)

    def visit_latex_comment_node(self, node: LatexCommentNode):
        pass

    def visit_latex_environment_node(self, node: LatexEnvironmentNode):
        if node.environmentname == 'figure':
            # prevent visiting image
            node.nodelist = []
            self._strings.append(IMAGE_PLACEHOLDER)

    def visit_latex_macro_node(self, node: LatexMacroNode):
        if node.macroname == 'includegraphics':
            self._strings.append(IMAGE_PLACEHOLDER)

    def visit_latex_math_node(self, node: LatexMathNode):
        self._strings.append(MATH_PLACEHOLDER)

    def visit_latex_specials_node(self, node: LatexSpecialsNode):
        pass
