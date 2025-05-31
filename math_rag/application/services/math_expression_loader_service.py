from logging import getLogger
from typing import TypeAlias
from uuid import UUID

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
from math_rag.application.models.assistants import (
    KatexCorrectorAssistantInput,
    KatexCorrectorAssistantOutput,
)
from math_rag.core.models import MathExpression


logger = getLogger(__name__)

MathNodeResultPair: TypeAlias = tuple[LatexMathNode, KatexValidationResult]
SplitValidationResult: TypeAlias = tuple[list[MathNodeResultPair], list[MathNodeResultPair]]


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

    async def load(self, dataset_id: UUID, foundation_dataset_id: UUID | None):
        # gather all .tex file names
        file_names = [
            name
            for name in self.math_article_repository.list_names()
            if name is not None and name.endswith('.tex')
        ]

        # load and parse math articles
        math_nodes: list[LatexMathNode] = []

        for file_name in file_names:
            math_article = self.math_article_repository.find_by_name(file_name)

            if foundation_dataset_id:
                if math_article.index_id != foundation_dataset_id:
                    continue

            elif math_article.index_id != dataset_id:
                continue

            math_nodes.extend(self.math_article_parser_service.parse(math_article))

        # extract and validate KaTeX
        katexes = [str(node.latex_verbatim()).strip('$') for node in math_nodes]
        results = await self.katex_client.batch_validate_many(katexes, batch_size=50)
        valid, invalid = self._split_by_validity(math_nodes, results)
        logger.info(f'Validated KaTeX: {len(valid)}/{len(results)}')

        # prepare final_katexes, preserving originals for valid ones
        final_katexes: list[str | None] = [
            katex if results[i].valid else None for i, katex in enumerate(katexes)
        ]

        if invalid:
            # create the inputs
            inputs: list[KatexCorrectorAssistantInput] = []
            invalid_input_id_to_node: dict[UUID, LatexMathNode] = {}

            for node, result in invalid:
                input = KatexCorrectorAssistantInput(
                    katex=str(node.latex_verbatim()).strip('$'),
                    error=result.error,
                )
                inputs.append(input)
                invalid_input_id_to_node[input.id] = node

            # call assistant (may return fewer outputs)
            outputs = await self.katex_corrector_assistant.batch_assist(inputs, use_scheduler=True)

            # map returned outputs back to nodes
            input_id_to_output: dict[UUID, KatexCorrectorAssistantOutput] = {
                output.input_id: output for output in outputs
            }

            # prepare lists for only those we actually got back
            corrected_katexes: list[str] = []
            corrected_nodes: list[LatexMathNode] = []

            for input_id, node in invalid_input_id_to_node.items():
                if input_id in input_id_to_output:
                    corrected_nodes.append(node)
                    corrected_katexes.append(input_id_to_output[input_id].katex)

            # re-validate only the ones we have corrections for
            re_results = await self.katex_client.batch_validate_many(
                corrected_katexes, batch_size=50
            )
            re_valid, _ = self._split_by_validity(corrected_nodes, re_results)

            # merge only the successfully re-validated corrections
            for node, corrected_katex, re_result in zip(
                corrected_nodes, corrected_katexes, re_results
            ):
                if re_result.valid:
                    idx = math_nodes.index(node)
                    final_katexes[idx] = corrected_katex

            num_corrected = len(re_valid)
            num_non_corrected = len(invalid) - num_corrected

            logger.info(
                f'Re-validated KaTeX: corrected {num_corrected} expressions, '
                f'still failing total {num_non_corrected} expressions'
            )

        # create and insert math expressions
        math_expressions: list[MathExpression] = []

        for node, katex in zip(math_nodes, final_katexes):
            math_expressions.append(
                MathExpression(
                    math_article_id=math_article.id,
                    math_expression_dataset_id=dataset_id,
                    latex=str(node.latex_verbatim()),
                    katex=katex,
                    position=node.pos,
                    is_inline=node.displaytype == 'inline',
                )
            )

        await self.math_expression_repository.batch_insert_many(math_expressions, batch_size=1000)
        await self.math_expression_repository.backup()
        logger.info(f'{self.__class__.__name__} loaded {len(math_expressions)} math expressions')
