from pylatexenc.latexwalker import LatexMathNode


class LatexMathRichNode(LatexMathNode):
    latex: str
    katex: str
