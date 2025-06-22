import re

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
)

from .base_latex_node_visitor import BaseLatexNodeVisitor


IMAGE_PLACEHOLDER_TEMPLATE = '[image_placeholder | {index}]'
MATH_PLACEHOLDER_TEMPLATE = '[math_placeholder | {index}]'
MATH_PLACEHOLDER_PATTERN = r'\[math_placeholder(?: \| \d+)?\]'


class TemplateHelper(BaseLatexNodeVisitor):
    def __init__(self):
        super().__init__()

        self._strings: list[str] = []
        self._num_image_nodes = 0
        self._num_math_nodes = 0

    @property
    def template(self) -> str:
        return str().join(self._strings)

    @property
    def positions(self) -> str:
        return [match.start() for match in re.finditer(MATH_PLACEHOLDER_PATTERN, self.template)]

    def visit_latex_chars_node(self, node: LatexCharsNode):
        self._strings.append(node.chars)

    def visit_latex_comment_node(self, node: LatexCommentNode):
        pass

    def visit_latex_environment_node(self, node: LatexEnvironmentNode):
        if node.environmentname == 'figure':
            # prevent visiting image
            node.nodelist = []

            image_placeholder = IMAGE_PLACEHOLDER_TEMPLATE.format(index=self._num_image_nodes)
            self._strings.append(image_placeholder)
            self._num_image_nodes += 1

    def visit_latex_macro_node(self, node: LatexMacroNode):
        if node.macroname == 'includegraphics':
            image_placeholder = IMAGE_PLACEHOLDER_TEMPLATE.format(index=self._num_image_nodes)
            self._strings.append(image_placeholder)
            self._num_image_nodes += 1

    def visit_latex_math_node(self, node: LatexMathNode):
        math_placeholder = MATH_PLACEHOLDER_TEMPLATE.format(index=self._num_math_nodes)
        self._strings.append(math_placeholder)
        self._num_math_nodes += 1

    def visit_latex_specials_node(self, node: LatexSpecialsNode):
        pass
