from typing import Iterator

from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexNode,
)

from math_rag.infrastructure.types.services import LatexNodeVisitor


class LatexNodeWalkerService:
    def walk(
        self,
        nodes: list[LatexNode],
        visitors: list[LatexNodeVisitor],
    ):
        stack: list[Iterator[LatexNode]] = [iter(nodes)]

        while stack:
            node = next(stack[-1], None)

            if node is None:
                stack.pop()
                continue

            node_type = type(node)

            for visitor in visitors:
                if node_type in visitor:
                    visit = visitor[node_type]
                    visit(node)

            if isinstance(node, (LatexEnvironmentNode, LatexGroupNode)):
                stack.append(iter(node.nodelist))
