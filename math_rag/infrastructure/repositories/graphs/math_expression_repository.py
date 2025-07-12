from math_rag.application.base.repositories.graphs import BaseMathExpressionRepository
from math_rag.core.models import MathExpression, MathExpressionRelationship
from math_rag.infrastructure.mappings.graphs import (
    MathExpressionMapping,
    MathExpressionRelationshipMapping,
)
from math_rag.infrastructure.models.graphs import MathExpressionNode, MathExpressionRel

from .graph_repository import GraphRepository


class MathExpressionRepository(
    BaseMathExpressionRepository,
    GraphRepository[
        MathExpression,
        MathExpressionRelationship,
        MathExpressionNode,
        MathExpressionRel,
        MathExpressionMapping,
        MathExpressionRelationshipMapping,
    ],
):
    def __init__(self):
        super().__init__(
            rel_field='related_to',
            source_node_id_field='math_expression_source_id',
            target_node_id_field='math_expression_target_id',
        )
