from deprecated import deprecated
from pylatexenc.latexwalker import LatexNode, LatexWalker, LatexWalkerParseError


class LatexParserService:
    @deprecated(reason='Tolerant parsing is neccessary, but sometimes gets stuck in a loop')
    def parse_deprecated(self, latex: str) -> list[LatexNode]:
        walker = LatexWalker(latex, tolerant_parsing=True)
        nodes, _, _ = walker.get_latex_nodes()

        return nodes

    def _parse_segment(
        self,
        latex: str,
        start: int,
        end: int,
        strict: bool,
    ) -> list[LatexNode]:
        segment = latex[start:end]
        walker = LatexWalker(segment, tolerant_parsing=not strict)

        try:
            nodes, _, _ = walker.get_latex_nodes()

            return nodes

        except LatexWalkerParseError:
            # if only one char remains, drop it
            if end - start <= 1:
                return []

            mid = start + (end - start) // 2

            # recurse on halves
            left = self._parse_segment(latex, start, mid, strict)
            right = self._parse_segment(latex, mid, end, strict)

            return left + right

    def parse(self, latex: str) -> list[LatexNode]:
        """
        Robust parsing: try strict on whole string, else divide-and-conquer.
        """
        try:
            return self._parse_segment(latex, 0, len(latex), strict=True)

        except Exception:
            return []
