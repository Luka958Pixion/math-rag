from uuid import UUID

from math_rag.core.models import MathExpressionGroupRelationship
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.graphs import MathExpressionGroupRel


class MathExpressionGroupRelationshipMapping(
    BaseMapping[MathExpressionGroupRelationship, MathExpressionGroupRel]
):
    @staticmethod
    def to_source(target: MathExpressionGroupRel) -> MathExpressionGroupRelationship:
        return MathExpressionGroupRelationship(
            id=UUID(target.uid),
            math_expression_index_id=UUID(target.math_expression_index_id),
            math_expression_id=UUID(target.math_expression_id),
            math_expression_group_id=UUID(target.math_expression_group_id),
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(source: MathExpressionGroupRelationship) -> MathExpressionGroupRel:
        return MathExpressionGroupRel(
            uid=str(source.id),
            math_expression_index_id=str(source.math_expression_index_id),
            math_expression_id=str(source.math_expression_id),
            math_expression_group_id=str(source.math_expression_group_id),
            timestamp=source.timestamp,
        )
