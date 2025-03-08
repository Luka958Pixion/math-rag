from uuid import UUID

from pydantic import BaseModel

from math_rag.core.models import MathExpressionClassification


class MathExpressionClassificationDocument(BaseModel):
    _id: UUID
    math_expression_id: UUID
    value: str

    @classmethod
    def from_internal(
        cls, inter: MathExpressionClassification
    ) -> 'MathExpressionClassificationDocument':
        return cls(
            _id=inter.id,
            math_expression_id=inter.math_expression_id,
            value=inter.value,
        )

    @classmethod
    def to_internal(
        cls, doc: 'MathExpressionClassificationDocument'
    ) -> MathExpressionClassification:
        return cls(
            id=doc._id,
            math_expression_id=doc.math_expression_id,
            value=doc.value,
        )
