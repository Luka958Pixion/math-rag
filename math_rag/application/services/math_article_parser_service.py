from copy import deepcopy

from pylatexenc.latexwalker import LatexMathNode

from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseLatexParserService,
    BaseLatexVisitorService,
    BaseMathArticleParserService,
)
from math_rag.application.extensions import LatexMathNodeRich
from math_rag.infrastructure.utils import FileReaderUtil


class MathArticleParserService(BaseMathArticleParserService):
    def __init__(
        self,
        latex_parser_service: BaseLatexParserService,
        latex_visitor_service: BaseLatexVisitorService,
        math_article_repository: BaseMathArticleRepository,
    ):
        self.latex_parser_service = latex_parser_service
        self.latex_visitor_service = latex_visitor_service
        self.math_article_repository = math_article_repository

    def parse(self):
        file_names = self.math_article_repository.list_names()
        file_names = [x for x in file_names if x.endswith('.tex')]
        math_nodes: list[LatexMathNodeRich] = []

        def append_math_node(math_node: LatexMathNode):
            latex = str(math_node.latex_verbatim())

            if 'tikz' not in latex and len(latex) < 1000:
                math_node_plus: LatexMathNodeRich = deepcopy(math_node)
                math_node_plus.__class__ = LatexMathNodeRich
                math_node_plus.latex = latex
                math_node_plus.katex = latex.strip('$')
                math_nodes.append(math_node_plus)

        for name in file_names:
            math_article = self.math_article_repository.find_by_name(name)
            latex = FileReaderUtil.read(math_article.bytes)
            nodes = self.latex_parser_service.parse(latex)
            callbacks = {LatexMathNode: append_math_node}

            self.latex_visitor_service.visit(nodes, callbacks)
