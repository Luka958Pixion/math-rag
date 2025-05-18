from logging import getLogger
from typing import TypeAlias

from pylatexenc.latexwalker import LatexMathNode

from math_rag.application.assistants import KatexCorrectorAssistant
from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseMathArticleParserService,
    BaseMathExpressionLoaderService,
)
from math_rag.application.models import KatexValidationResult
from math_rag.application.models.assistants import KatexCorrectorAssistantInput
from math_rag.core.models import MathExpression


logger = getLogger(__name__)

MathNodeResultPair: TypeAlias = tuple[LatexMathNode, KatexValidationResult]
SplitValidationResult: TypeAlias = tuple[
    list[MathNodeResultPair], list[MathNodeResultPair]
]


class MathExpressionLoaderService(BaseMathExpressionLoaderService):
    def __init__(
        self,
        katex_client: BaseKatexClient,
        katex_corrector_assistant: KatexCorrectorAssistant,
        math_article_parser_service: BaseMathArticleParserService,
        math_article_repository: BaseMathArticleRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.katex_client = katex_client
        self.katex_corrector_assistant = katex_corrector_assistant
        self.math_article_parser_service = math_article_parser_service
        self.math_article_repository = math_article_repository
        self.math_expression_repository = math_expression_repository

    def _split_by_validity(
        self,
        nodes: list[LatexMathNode],
        results: list[KatexValidationResult],
    ) -> SplitValidationResult:
        valid: list[MathNodeResultPair] = []
        invalid: list[MathNodeResultPair] = []

        for node, result in zip(nodes, results):
            (valid if result.valid else invalid).append((node, result))

        return valid, invalid

    async def load(self):
        # gather all .tex file names
        file_names = [
            name
            for name in self.math_article_repository.list_names()
            if name is not None and name.endswith('.tex')
        ]

        for name in file_names:
            # load and parse math articles
            math_article = await self.math_article_repository.find_by_name(name)
            math_nodes = self.math_article_parser_service.parse(math_article)

            # extract raw KaTeX strings
            katexes = [str(node.latex_verbatim()).strip('$') for node in math_nodes]

            # validate KaTeX
            results = await self.katex_client.batch_validate_many(
                katexes, batch_size=1000
            )
            valid, invalid = self._split_by_validity(math_nodes, results)
            logger.info(f'Validated KaTeX: {len(valid)}/{len(results)}')

            # attempt correction if any failed
            if invalid:
                inputs = [
                    KatexCorrectorAssistantInput(
                        katex=str(node.latex_verbatim()).strip('$'),
                        error=result.error,
                    )
                    for node, result in invalid
                ]
                outputs = await self.katex_corrector_assistant.batch_assist(inputs)
                corrected_katexes = [output.katex for output in outputs]

                # re-validate corrected KaTeX
                re_results = await self.katex_client.batch_validate_many(
                    corrected_katexes, batch_size=1000
                )
                re_valid, re_invalid = self._split_by_validity(
                    [node for node, _ in invalid],
                    re_results,
                )

                # merge results
                valid.extend(re_valid)
                invalid = re_invalid

                logger.info(
                    f'Re-validated KaTeX: recovered {len(re_valid)}, still failing {len(invalid)}'
                )

            # create and insert math expressions
            math_expressions: list[MathExpression] = []

            for math_node, result in valid + invalid:
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

        await self.math_expression_repository.backup()
