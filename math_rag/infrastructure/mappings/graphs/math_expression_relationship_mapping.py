from uuid import UUID

from math_rag.core.models import MathExpressionRelationship
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.graphs import MathExpressionRel


class MathExpressionRelationshipMapping(BaseMapping[MathExpressionRelationship, MathExpressionRel]):
    @staticmethod
    def to_source(target: MathExpressionRel) -> MathExpressionRelationship:
        return MathExpressionRelationship(
            id=UUID(target.id),
            math_expression_index_id=UUID(target.math_expression_index_id),
            math_expression_source_id=UUID(target.math_expression_source_id),
            math_expression_target_id=UUID(target.math_expression_target_id),
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(source: MathExpressionRelationship) -> MathExpressionRel:
        return MathExpressionRel(
            id=str(source.id),
            math_expression_index_id=str(source.math_expression_index_id)
            if source.math_expression_index_id
            else None,
            math_expression_source_id=str(source.math_expression_source_id)
            if source.math_expression_source_id
            else None,
            math_expression_target_id=str(source.math_expression_target_id)
            if source.math_expression_target_id
            else None,
            timestamp=source.timestamp,
        )
