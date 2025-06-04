from pylatexenc.latexwalker import LatexEnvironmentNode

from math_rag.application.base.services import BaseMathArticleParserService
from math_rag.core.models import LatexMathNode, MathArticle
from math_rag.infrastructure.services import LatexNodeWalkerService, LatexParserService
from math_rag.infrastructure.utils import FileReaderUtil

from .helpers import LatexMathNodeHelper, TemplateHelper


class MathArticleParserService(BaseMathArticleParserService):
    def __init__(
        self,
        latex_parser_service: LatexParserService,
        latex_node_walker_service: LatexNodeWalkerService,
    ):
        self.latex_parser_service = latex_parser_service
        self.latex_node_walker_service = latex_node_walker_service

    def parse_for_dataset(self, math_article: MathArticle) -> list[LatexMathNode]:
        helper = LatexMathNodeHelper()
        latex = FileReaderUtil.read(math_article.bytes)
        nodes = self.latex_parser_service.parse(latex)
        self.latex_node_walker_service.walk(nodes, [helper.visitor])

        return [
            LatexMathNode(latex=latex, position=node.pos, is_inline=node.displaytype == 'inline')
            for node in helper.math_nodes
        ]

    def parse_for_index(
        self, math_article: MathArticle
    ) -> tuple[list[LatexMathNode], list[int], str]:
        latex_math_node_helper = LatexMathNodeHelper()
        template_helper = TemplateHelper()
        latex = FileReaderUtil.read(math_article.bytes)

        nodes = self.latex_parser_service.parse(latex)
        doc_env_nodes = (
            node
            for node in nodes
            if isinstance(node, LatexEnvironmentNode) and node.environmentname == 'document'
        )
        doc_env_node = next(doc_env_nodes, None)

        if doc_env_node:
            nodes = doc_env_node.nodelist

        self.latex_node_walker_service.walk(
            nodes, [latex_math_node_helper.visitor, template_helper.visitor]
        )
        latex_math_nodes = [
            LatexMathNode(latex=latex, position=node.pos, is_inline=node.displaytype == 'inline')
            for node in latex_math_node_helper.math_nodes
        ]

        return latex_math_nodes, template_helper.positions, template_helper.template
