from pylatexenc.latexwalker import (
    LatexNode,
    LatexWalker,
)


class LatexParserService:
    def parse(self, latex: str) -> list[LatexNode]:
        walker = LatexWalker(latex)
        nodes, _, _ = walker.get_latex_nodes()

        return nodes
