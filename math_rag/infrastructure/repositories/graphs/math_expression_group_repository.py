from math_rag.application.base.repositories.graphs import BaseMathExpressionGroupRepository
from math_rag.core.models import MathExpressionGroup, MathExpressionGroupRelationship
from math_rag.infrastructure.mappings.graphs import (
    MathExpressionGroupMapping,
    MathExpressionGroupRelationshipMapping,
)
from math_rag.infrastructure.models.graphs import MathExpressionGroupNode, MathExpressionGroupRel

from .graph_repository import GraphRepository


class MathExpressionGroupRepository(
    BaseMathExpressionGroupRepository,
    GraphRepository[
        MathExpressionGroup,
        MathExpressionGroupRelationship,
        MathExpressionGroupNode,
        MathExpressionGroupRel,
        MathExpressionGroupMapping,
        MathExpressionGroupRelationshipMapping,
    ],
):
    def __init__(self):
        super().__init__(
            rel_field='member_of',
            source_node_id_field='math_expression_group_id',
            target_node_id_field='math_expression_id',
        )
