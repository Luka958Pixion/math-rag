from math_rag.core.models import MathExpressionClassification
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)


class MathExpressionClassificationMapping(
    BaseMapping[MathExpressionClassification, MathExpressionClassificationDocument]
):
    @staticmethod
    def to_source(
        target: MathExpressionClassificationDocument,
    ) -> MathExpressionClassification:
        source = MathExpressionClassification(
            id=target._id,
            math_expression_id=target.math_expression_id,
            value=target.value,
        )

        return source

    @staticmethod
    def to_target(
        source: MathExpressionClassification,
    ) -> MathExpressionClassificationDocument:
        target = MathExpressionClassificationDocument(
            _id=source.id,
            math_expression_id=source.math_expression_id,
            value=source.value,
        )

        return target
