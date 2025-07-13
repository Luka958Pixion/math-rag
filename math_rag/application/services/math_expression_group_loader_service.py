from logging import getLogger

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionGroupRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptRepository as BaseMathExpressionDescriptionOptEmbeddingRepository,
)
from math_rag.application.base.repositories.graphs import (
    BaseMathExpressionGroupRepository as BaseMathExpressionGroupGraphRepository,
    BaseMathExpressionRepository as BaseMathExpressionGraphRepository,
)
from math_rag.application.base.services import (
    BaseGrouperService,
    BaseMathExpressionGroupLoaderService,
)
from math_rag.core.models import MathExpressionGroup, MathExpressionIndex


logger = getLogger(__name__)


class MathExpressionGroupLoaderService(BaseMathExpressionGroupLoaderService):
    def __init__(
        self,
        grouper_service: BaseGrouperService,
        math_expression_description_opt_embedding_repository: BaseMathExpressionDescriptionOptEmbeddingRepository,
        math_expression_group_graph_repository: BaseMathExpressionGroupGraphRepository,
        math_expression_group_repository: BaseMathExpressionGroupRepository,
        math_expression_graph_repository: BaseMathExpressionGraphRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.grouper_service = grouper_service
        self.math_expression_description_opt_embedding_repository = (
            math_expression_description_opt_embedding_repository
        )
        self.math_expression_group_graph_repository = math_expression_group_graph_repository
        self.math_expression_group_repository = math_expression_group_repository
        self.math_expression_graph_repository = math_expression_graph_repository
        self.math_expression_repository = math_expression_repository

    async def load_for_index(self, index: MathExpressionIndex):
        # math expression descriptions
        grouped_descriptions = (
            await self.math_expression_description_opt_embedding_repository.group(
                self.grouper_service.group
            )
        )

        # math expression groups
        grouped_math_expression_ids = [
            [description.math_expression_id for description in descriptions]
            for descriptions in grouped_descriptions
        ]
        num_math_expression_groups = 0

        for math_expression_ids in grouped_math_expression_ids:
            # group requires at least two elements
            if len(math_expression_ids) < 2:
                continue

            math_expression_group = MathExpressionGroup(math_expression_index_id=index.id)
            await self.math_expression_group_repository.insert_one(math_expression_group)
            await self.math_expression_group_graph_repository.insert_one_node(math_expression_group)

            # add all candidates to a group, remove some of them in the next step
            await self.math_expression_repository.update_group_id(
                math_expression_ids, math_expression_group.id
            )
            await self.math_expression_graph_repository.update_many_nodes(
                filter=dict(id=math_expression_ids),
                update=dict(math_expression_group_id=math_expression_group.id),
            )
            num_math_expression_groups += 1

        logger.info(
            f'{self.__class__.__name__} loaded {num_math_expression_groups} math expression groups'
        )
