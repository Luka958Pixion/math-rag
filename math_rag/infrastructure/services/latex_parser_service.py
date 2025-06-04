from deprecated import deprecated
from pylatexenc.latexwalker import LatexNode, LatexWalker, LatexWalkerParseError


class LatexParserService:
    @deprecated(reason='Tolerant parsing is neccessary, but sometimes gets stuck in a loop')
    def parse_deprecated(self, latex: str) -> list[LatexNode]:
        walker = LatexWalker(latex, tolerant_parsing=True)
        nodes, _, _ = walker.get_latex_nodes()

        return nodes

    def parse(self, latex: str) -> list[LatexNode]:
        walker = LatexWalker(latex, tolerant_parsing=False)
        nodes: list[LatexNode] = []
        position = 0
        length = len(latex)

        while position < length:
            try:
                # read exactly one top-level node at a time
                new_nodes, new_position, _ = walker.get_latex_nodes(pos=position, read_max_nodes=1)

                # guard against no forward progress
                if new_position <= position:
                    new_position = position + 1

                nodes.extend(new_nodes)
                position = new_position

            except LatexWalkerParseError:
                # skip the problematic character and continue
                position += 1

        return nodes
