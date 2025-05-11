from pylatexenc.latexwalker import LatexMathNode


class LatexMathNodeRich(LatexMathNode):
    latex: str
    katex: str
