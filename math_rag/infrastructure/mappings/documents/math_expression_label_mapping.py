from math_rag.core.models import MathExpressionLabel
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import (
    MathExpressionLabelDocument,
)


class MathExpressionLabelMapping(
    BaseMapping[MathExpressionLabel, MathExpressionLabelDocument]
):
    @staticmethod
    def to_source(
        target: MathExpressionLabelDocument,
    ) -> MathExpressionLabel:
        return MathExpressionLabel(
            id=target.id,
            timestamp=target.timestamp,
            math_expression_id=target.math_expression_id,
            value=target.value,
        )

    @staticmethod
    def to_target(
        source: MathExpressionLabel,
    ) -> MathExpressionLabelDocument:
        return MathExpressionLabelDocument(
            id=source.id,
            timestamp=source.timestamp,
            math_expression_id=source.math_expression_id,
            value=source.value,
        )
