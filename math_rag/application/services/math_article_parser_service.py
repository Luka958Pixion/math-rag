from pylatexenc.latexwalker import LatexMathNode

from math_rag.application.base.services import (
    BaseLatexParserService,
    BaseLatexVisitorService,
    BaseMathArticleParserService,
)
from math_rag.core.models import MathArticle
from math_rag.infrastructure.utils import FileReaderUtil


class MathArticleParserService(BaseMathArticleParserService):
    def __init__(
        self,
        latex_parser_service: BaseLatexParserService,
        latex_visitor_service: BaseLatexVisitorService,
    ):
        self.latex_parser_service = latex_parser_service
        self.latex_visitor_service = latex_visitor_service

    def parse(self, math_article: MathArticle) -> list[LatexMathNode]:
        math_nodes: list[LatexMathNode] = []

        def append_math_node(math_node: LatexMathNode):
            latex = str(math_node.latex_verbatim())

            if 'tikz' not in latex and len(latex) < 1000:
                math_nodes.append(math_node)

        latex = FileReaderUtil.read(math_article.bytes)
        nodes = self.latex_parser_service.parse(latex)
        callbacks = {LatexMathNode: append_math_node}

        self.latex_visitor_service.visit(nodes, callbacks)

        return math_nodes
