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
            math_article = self.math_article_repository.find_by_name(name)
            math_nodes = self.math_article_parser_service.parse(math_article)

            # extract and validate KaTeX
            katexes = [str(node.latex_verbatim()).strip('$') for node in math_nodes]
            results = await self.katex_client.batch_validate_many(
                katexes, batch_size=1000
            )
            valid, invalid = self._split_by_validity(math_nodes, results)
            logger.info(f'Validated KaTeX: {len(valid)}/{len(results)}')

            # try to correct invalid KaTeX
            final_katexes: list[str | None] = [
                katex if results[i].valid else None for i, katex in enumerate(katexes)
            ]

            if invalid:
                correction_inputs = [
                    KatexCorrectorAssistantInput(
                        katex=str(node.latex_verbatim()).strip('$'),
                        error=result.error,
                    )
                    for node, result in invalid
                ]
                outputs = await self.katex_corrector_assistant.concurrent_assist(
                    correction_inputs
                )
                corrected_katexes = [output.katex for output in outputs]

                re_results = await self.katex_client.batch_validate_many(
                    corrected_katexes, batch_size=1000
                )
                re_valid, re_invalid = self._split_by_validity(
                    [node for node, _ in invalid],
                    re_results,
                )

                # merge corrected into final_katexes
                for (node, _), corrected_katex, re_result in zip(
                    invalid, corrected_katexes, re_results
                ):
                    if re_result.valid:
                        index = math_nodes.index(node)
                        final_katexes[index] = corrected_katex

                logger.info(
                    f'Re-validated KaTeX: recovered {len(re_valid)}, still failing {len(re_invalid)}'
                )

            # create and insert math expressions
            math_expressions: list[MathExpression] = []

            for node, katex in zip(math_nodes, final_katexes):
                latex = str(node.latex_verbatim())
                math_expressions.append(
                    MathExpression(
                        math_article_id=math_article.id,
                        latex=latex,
                        katex=katex,
                        position=node.pos,
                        is_inline=node.displaytype == 'inline',
                    )
                )

            await self.math_expression_repository.batch_insert_many(
                math_expressions, batch_size=100
            )

        await self.math_expression_repository.backup()
