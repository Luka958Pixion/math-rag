from math_rag.core.models import MathExpressionDescription
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDescriptionDocument


class MathExpressionDescriptionMapping(
    BaseMapping[MathExpressionDescription, MathExpressionDescriptionDocument]
):
    @staticmethod
    def to_source(target: MathExpressionDescriptionDocument) -> MathExpressionDescription:
        return MathExpressionDescription(
            id=target.id,
            math_expression_id=target.math_expression_id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
            text=target.text,
        )

    @staticmethod
    def to_target(source: MathExpressionDescription) -> MathExpressionDescriptionDocument:
        return MathExpressionDescriptionDocument(
            id=source.id,
            math_expression_id=source.math_expression_id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
            text=source.text,
        )
