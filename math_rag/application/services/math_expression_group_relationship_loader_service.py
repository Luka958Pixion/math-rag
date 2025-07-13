from itertools import combinations
from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionComparatorAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionContextRepository,
    BaseMathExpressionGroupRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.graphs import (
    BaseMathExpressionGroupRepository as BaseMathExpressionGroupGraphRepository,
    BaseMathExpressionRepository as BaseMathExpressionGraphRepository,
)
from math_rag.application.base.services import BaseMathExpressionGroupRelationshipLoaderService
from math_rag.application.models.assistants.inputs import MathExpressionComparator as AssistantInput
from math_rag.application.utils import GroupPrunerUtil
from math_rag.core.models import (
    MathExpression,
    MathExpressionGroupRelationship,
    MathExpressionIndex,
)


logger = getLogger(__name__)


class MathExpressionGroupRelationshipLoaderService(
    BaseMathExpressionGroupRelationshipLoaderService
):
    def __init__(
        self,
        math_expression_comparator_assistant: MathExpressionComparatorAssistant,
        math_expression_context_repository: BaseMathExpressionContextRepository,
        math_expression_group_graph_repository: BaseMathExpressionGroupGraphRepository,
        math_expression_group_repository: BaseMathExpressionGroupRepository,
        math_expression_graph_repository: BaseMathExpressionGraphRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.math_expression_comparator_assistant = math_expression_comparator_assistant
        self.math_expression_context_repository = math_expression_context_repository
        self.math_expression_group_graph_repository = math_expression_group_graph_repository
        self.math_expression_group_repository = math_expression_group_repository
        self.math_expression_graph_repository = math_expression_graph_repository
        self.math_expression_repository = math_expression_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math expression groups
        math_expression_groups = await self.math_expression_group_repository.find_many(
            filter=index_filter
        )

        # math expression group relationships
        num_group_relationships = 0

        for math_expression_group in math_expression_groups:
            math_expressions = await self.math_expression_repository.find_many(
                filter=dict(math_expression_group_id=math_expression_group.id)
            )
            math_expression_ids = [math_expression.id for math_expression in math_expressions]
            math_expression_contexts = await self.math_expression_context_repository.find_many(
                filter=dict(math_expression_id=math_expression_ids)
            )
            pairs = list(combinations(zip(math_expressions, math_expression_contexts), 2))

            # logger.info(len(math_expressions))
            # logger.info(len(pairs))
            # logger.info()

            if not pairs:
                continue

            inputs: list[AssistantInput] = []
            input_id_to_candidate_pair: dict[UUID, tuple[UUID, UUID]] = {}

            for pair, other_pair in pairs:
                math_expression, math_expression_context = pair
                other_math_expression, other_math_expression_context = other_pair
                input = AssistantInput(
                    katex=math_expression.katex,
                    context=math_expression_context.text,
                    other_katex=other_math_expression.katex,
                    other_context=other_math_expression_context.text,
                )
                inputs.append(input)
                input_id_to_candidate_pair[input.id] = (
                    math_expression.id,
                    other_math_expression.id,
                )

            outputs = await self.math_expression_comparator_assistant.concurrent_assist(inputs)

            candidates = math_expression_ids
            candidate_pair_to_is_connected = {
                input_id_to_candidate_pair[output.input_id]: output.is_identical
                for output in outputs
            }

            math_expression_ids = [math_expression.id for math_expression in math_expressions]
            math_expression_ids_to_group = GroupPrunerUtil.prune(
                candidates, candidate_pair_to_is_connected
            )
            math_expression_ids_to_ungroup = list(
                set(math_expression_ids) - set(math_expression_ids_to_group)
            )

            if not math_expression_ids_to_group:
                continue

            math_expression_group_relationships = [
                MathExpressionGroupRelationship(
                    math_expression_index_id=index.id,
                    math_expression_id=math_expression_id,
                    math_expression_group_id=math_expression_group.id,
                )
                for math_expression_id in math_expression_ids_to_group
            ]
            await self.math_expression_repository.update_group_id(
                math_expression_ids_to_ungroup, None
            )
            await self.math_expression_graph_repository.update_many_nodes(
                filter=dict(id=math_expression_ids_to_ungroup),
                update=dict(math_expression_group_id=None),
            )

            math_expression_group_relationships = [
                MathExpressionGroupRelationship(
                    math_expression_index_id=index.id,
                    math_expression_id=math_expression_id,
                    math_expression_group_id=math_expression_group.id,
                )
                for math_expression_id in math_expression_ids_to_group
            ]
            num_group_relationships += len(math_expression_group_relationships)

            # logger.info(len(math_expression_ids))
            # logger.info(len(math_expression_ids_to_group))
            # logger.info(len(math_expression_ids_to_ungroup))
            # logger.info(len(math_expression_group_relationships))
            # logger.info()

            await self.math_expression_group_graph_repository.insert_many_rels(
                math_expression_group_relationships, rel_to_cls=MathExpression
            )

        logger.info(
            f'{self.__class__.__name__} loaded '
            f'{num_group_relationships} math expression group relationships'
        )
