from math_rag.core.models import MathExpressionGroup
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionGroupDocument


class MathExpressionGroupMapping(BaseMapping[MathExpressionGroup, MathExpressionGroupDocument]):
    @staticmethod
    def to_source(target: MathExpressionGroupDocument) -> MathExpressionGroup:
        return MathExpressionGroup(
            id=target.id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(source: MathExpressionGroup) -> MathExpressionGroupDocument:
        return MathExpressionGroupDocument(
            id=source.id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
        )
