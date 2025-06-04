from typing import Callable, Iterator

from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexNode,
)

from math_rag.application.base.services import BaseLatexVisitorService


class LatexVisitorService(BaseLatexVisitorService):
    def visit(
        self,
        nodes: list[LatexNode],
        callbacks: dict[type[LatexNode], Callable[[LatexNode], None]],
    ):
        stack: list[Iterator[LatexNode]] = [iter(nodes)]

        while stack:
            node = next(stack[-1], None)

            if node is None:
                stack.pop()
                continue

            node_type = type(node)

            if node_type in callbacks:
                callbacks[node_type](node)

            if isinstance(node, (LatexEnvironmentNode, LatexGroupNode)):
                stack.append(iter(node.nodelist))
