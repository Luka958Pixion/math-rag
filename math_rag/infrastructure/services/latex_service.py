from io import BytesIO
from pathlib import Path
from typing import Callable, Iterator

from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexNode,
    LatexWalker,
)


class LatexService:
    def read(self, file: Path | bytes) -> str:
        for encoding in ('utf-8', 'latin1', 'cp1252'):
            try:
                if isinstance(file, Path):
                    with open(file, 'r', encoding=encoding) as f:
                        return f.read()

                elif isinstance(file, bytes):
                    return file.decode(encoding)

            except UnicodeDecodeError:
                continue

    def parse(self, latex: str) -> list[LatexNode]:
        walker = LatexWalker(latex)
        nodes, _, _ = walker.get_latex_nodes()

        return nodes

    def traverse(
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
