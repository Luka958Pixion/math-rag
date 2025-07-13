from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionRelationshipDetectorAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathArticleChunkRepository,
    BaseMathExpressionRelationshipRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.graphs import (
    BaseMathExpressionRepository as BaseMathExpressionGraphRepository,
)
from math_rag.application.base.services import BaseMathExpressionRelationshipLoaderService
from math_rag.application.models.assistants.inputs import (
    MathExpressionRelationshipDetector as AssistantInput,
)
from math_rag.core.models import MathExpressionIndex, MathExpressionRelationship


logger = getLogger(__name__)


class MathExpressionRelationshipLoaderService(BaseMathExpressionRelationshipLoaderService):
    def __init__(
        self,
        math_expression_relationship_detector_assistant: MathExpressionRelationshipDetectorAssistant,
        math_article_chunk_repository: BaseMathArticleChunkRepository,
        math_expression_graph_repository: BaseMathExpressionGraphRepository,
        math_expression_relationship_repository: BaseMathExpressionRelationshipRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.math_expression_relationship_detector_assistant = (
            math_expression_relationship_detector_assistant
        )
        self.math_article_chunk_repository = math_article_chunk_repository
        self.math_expression_graph_repository = math_expression_graph_repository
        self.math_expression_relationship_repository = math_expression_relationship_repository
        self.math_expression_repository = math_expression_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math expressions
        math_expressions = await self.math_expression_repository.find_many(filter=index_filter)

        # math article chunks
        math_article_chunks = await self.math_article_chunk_repository.find_many(
            filter=index_filter
        )

        # math expression relationships
        num_relationships = 0

        for math_article_chunk in math_article_chunks:
            if len(math_article_chunk.indexes) < 2:
                continue

            start_indexes = math_article_chunk.indexes[:-1]
            last_index = math_article_chunk.indexes[-1]
            index_pairs = [(index, last_index) for index in start_indexes]

            inputs: list[AssistantInput] = []
            input_id_to_math_expression_id_pair: dict[UUID, tuple[UUID, UUID]] = {}
            input_id_to_math_expression_index_pair: dict[UUID, tuple[int, int]] = {}

            for source_index, target_index in index_pairs:
                input = AssistantInput(
                    chunk=math_article_chunk.text, source=source_index, target=target_index
                )
                inputs.append(input)

                source_math_expression = next(
                    (x for x in math_expressions if x.index == source_index), None
                )
                target_math_expression = next(
                    (x for x in math_expressions if x.index == target_index), None
                )

                if source_math_expression is None or target_math_expression is None:
                    raise ValueError()

                input_id_to_math_expression_id_pair[input.id] = (
                    source_math_expression.id,
                    target_math_expression.id,
                )
                input_id_to_math_expression_index_pair[input.id] = source_index, target_index

            outputs = await self.math_expression_relationship_detector_assistant.concurrent_assist(
                inputs
            )
            math_expression_relationships = [
                MathExpressionRelationship(
                    math_article_chunk_id=math_article_chunk.id,
                    math_expression_index_id=index.id,
                    math_expression_source_id=input_id_to_math_expression_id_pair[output.input_id][
                        0
                    ],
                    math_expression_target_id=input_id_to_math_expression_id_pair[output.input_id][
                        1
                    ],
                    math_expression_source_index=input_id_to_math_expression_index_pair[
                        output.input_id
                    ][0],
                    math_expression_target_index=input_id_to_math_expression_index_pair[
                        output.input_id
                    ][1],
                )
                for output in outputs
                if output.relationship_exists
            ]
            num_relationships += len(math_expression_relationships)

            # logger.info(len(outputs))
            # logger.info(len(math_expression_relationships))
            # logger.info()

            await self.math_expression_relationship_repository.insert_many(
                math_expression_relationships
            )
            await self.math_expression_graph_repository.insert_many_rels(
                math_expression_relationships, rel_to_cls=None
            )

        logger.info(
            f'{self.__class__.__name__} loaded '
            f'{num_relationships} math expression relationships'
        )
