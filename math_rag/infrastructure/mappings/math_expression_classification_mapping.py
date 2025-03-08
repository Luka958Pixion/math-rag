from math_rag.core.models import MathExpressionClassification
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)


class MathExpressionClassificationMapping(
    BaseMapping[MathExpressionClassification, MathExpressionClassificationDocument]
):
    @classmethod
    def to_source(
        cls, target: MathExpressionClassificationDocument
    ) -> MathExpressionClassification:
        return cls(
            id=target._id,
            math_expression_id=target.math_expression_id,
            value=target.value,
        )

    @classmethod
    def to_target(
        cls, source: MathExpressionClassification
    ) -> MathExpressionClassificationDocument:
        return cls(
            _id=source.id,
            math_expression_id=source.math_expression_id,
            value=source.value,
        )
