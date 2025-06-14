from logging import getLogger
from typing import TypeAlias
from uuid import UUID

from math_rag.application.assistants import KatexCorrectorAssistant
from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.repositories.documents import BaseMathExpressionRepository
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseMathArticleParserService,
    BaseMathExpressionLoaderService,
)
from math_rag.application.models import KatexValidationResult
from math_rag.application.models.assistants import (
    KatexCorrectorAssistantInput,
)
from math_rag.core.enums import MathExpressionDatasetBuildPriority
from math_rag.core.models import Index, LatexMathNode, MathExpression, MathExpressionDataset


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

    async def load_for_dataset(self, dataset: MathExpressionDataset):
        # load and parse math articles
        dataset_id = dataset.build_from_id if dataset.build_from_id else dataset.id
        math_articles = await self.math_article_repository.find_many_by_math_expression_dataset_id(
            dataset_id
        )

        if not math_articles:
            raise ValueError(f'Math articles with dataset id {dataset_id} not found')

        math_nodes: list[LatexMathNode] = []

        for math_article in math_articles:
            if not math_article.name.endswith('.tex'):
                continue

            math_nodes_ = self.math_article_parser_service.parse_for_dataset(math_article)
            math_nodes.extend(math_nodes_)
            logger.info(f'Parsed {len(math_nodes_)} math nodes from {math_article.id}')

        # extract and validate KaTeX
        katexes = [node.latex.strip('$') for node in math_nodes]
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
            input_id_to_node: dict[UUID, LatexMathNode] = {}

            for node, result in invalid:
                input = KatexCorrectorAssistantInput(
                    katex=node.latex.strip('$'),
                    error=result.error,
                )
                inputs.append(input)
                input_id_to_node[input.id] = node

            match dataset.build_priority:
                case MathExpressionDatasetBuildPriority.COST:
                    outputs = await self.katex_corrector_assistant.batch_assist(
                        inputs, use_scheduler=True
                    )

                case MathExpressionDatasetBuildPriority.TIME:
                    outputs = await self.katex_corrector_assistant.concurrent_assist(inputs)

                case _:
                    raise ValueError(f'Build priority {dataset.build_priority} is not available')

            corrected_katexes = [output.katex for output in outputs]
            corrected_nodes = [input_id_to_node[output.input_id] for output in outputs]

            re_results = await self.katex_client.batch_validate_many(
                corrected_katexes, batch_size=50
            )
            re_valid, _ = self._split_by_validity(corrected_nodes, re_results)

            # merge only the successfully re-validated corrections
            for node, katex, result in zip(corrected_nodes, corrected_katexes, re_results):
                if result.valid:
                    index = math_nodes.index(node)
                    final_katexes[index] = katex

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
                    index_id=None,
                    latex=node.latex,
                    katex=katex,
                    position=node.position,
                    is_inline=node.is_inline,
                )
            )

        await self.math_expression_repository.batch_insert_many(math_expressions, batch_size=1000)
        await self.math_expression_repository.backup()
        logger.info(f'{self.__class__.__name__} loaded {len(math_expressions)} math expressions')

    async def load_for_index(self, index: Index):
        # load and parse math articles
        math_articles = await self.math_article_repository.find_many_by_index_id(index.id)

        if not math_articles:
            raise ValueError(f'Math articles with index id {index.id} not found')

        math_nodes: list[LatexMathNode] = []

        for math_article in math_articles:
            if not math_article.name.endswith('.tex'):
                continue

            # TODO
            math_nodes_, positions, template = self.math_article_parser_service.parse_for_index(
                math_article
            )
            math_nodes.extend(math_nodes_)
            logger.info(f'Parsed {len(math_nodes_)} math nodes from {math_article.id}')

        # extract and validate KaTeX
        katexes = [node.latex.strip('$') for node in math_nodes]
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
            input_id_to_node: dict[UUID, LatexMathNode] = {}

            for node, result in invalid:
                input = KatexCorrectorAssistantInput(
                    katex=node.latex.strip('$'),
                    error=result.error,
                )
                inputs.append(input)
                input_id_to_node[input.id] = node

            outputs = await self.katex_corrector_assistant.concurrent_assist(inputs)
            corrected_katexes = [output.katex for output in outputs]
            corrected_nodes = [input_id_to_node[output.input_id] for output in outputs]

            re_results = await self.katex_client.batch_validate_many(
                corrected_katexes, batch_size=50
            )
            re_valid, _ = self._split_by_validity(corrected_nodes, re_results)

            # merge only the successfully re-validated corrections
            for node, katex, result in zip(corrected_nodes, corrected_katexes, re_results):
                if result.valid:
                    index = math_nodes.index(node)
                    final_katexes[index] = katex

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
                    math_expression_dataset_id=None,
                    index_id=index.id,
                    latex=node.latex,
                    katex=katex,
                    position=node.position,
                    is_inline=node.is_inline,
                )
            )

        await self.math_expression_repository.batch_insert_many(math_expressions, batch_size=1000)
        await self.math_expression_repository.backup()
        logger.info(f'{self.__class__.__name__} loaded {len(math_expressions)} math expressions')
