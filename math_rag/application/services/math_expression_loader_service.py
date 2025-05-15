from logging import getLogger

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import BaseMathArticleParserService
from math_rag.core.models import MathExpression


logger = getLogger(__name__)


class MathExpressionLoaderService:  # TODO finish this + base class + DI
    def __init__(
        self,
        katex_client: BaseKatexClient,
        math_article_parser_service: BaseMathArticleParserService,
        math_article_repository: BaseMathArticleRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.katex_client = katex_client
        self.math_article_parser_service = math_article_parser_service
        self.math_article_repository = math_article_repository
        self.math_expression_repository = math_expression_repository

    async def load(self):
        file_names = [
            name
            for name in self.math_article_repository.list_names()
            if name.endswith('.tex')
        ]

        for name in file_names:
            math_article = self.math_article_repository.find_by_name(name)
            math_nodes = self.math_article_parser_service.parse(math_article)

            katexes: list[str] = []

            for math_node in math_nodes:
                latex = str(math_node.latex_verbatim())
                katex = latex.strip('$')
                katexes.append(katex)

            results = await self.katex_client.batch_validate_many(
                katexes, batch_size=1000
            )
            math_node_validation_results = list(zip(math_nodes, results))

            num_valid_results = sum(1 for result in results if result.valid)
            num_total_results = len(results)
            logger.info(f'Validated KaTeX: {num_valid_results}/{num_total_results}')

            math_expressions: list[MathExpression] = []

            for math_node, result in math_node_validation_results:
                latex = str(math_node.latex_verbatim())
                katex = latex.strip('$') if result.valid else None
                math_expression = MathExpression(
                    latex=latex,
                    katex=katex,
                    position=math_node.pos,
                    is_inline=math_node.displaytype == 'inline',
                )
                math_expressions.append(math_expression)

            await self.math_expression_repository.batch_insert_many(
                math_expressions, batch_size=100
            )
