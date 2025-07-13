from uuid import UUID

from math_rag.core.models import MathExpressionGroup
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.graphs import MathExpressionGroupNode


class MathExpressionGroupMapping(BaseMapping[MathExpressionGroup, MathExpressionGroupNode]):
    @staticmethod
    def to_source(target: MathExpressionGroupNode) -> MathExpressionGroup:
        return MathExpressionGroup(
            id=UUID(target.uid),
            math_expression_index_id=UUID(target.math_expression_index_id),
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(source: MathExpressionGroup) -> MathExpressionGroupNode:
        return MathExpressionGroupNode(
            uid=str(source.id),
            math_expression_index_id=str(source.math_expression_index_id),
            timestamp=source.timestamp,
        )
