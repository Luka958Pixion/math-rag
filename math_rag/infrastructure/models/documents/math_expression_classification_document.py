from uuid import UUID

from pydantic import BaseModel

from math_rag.core.models import MathExpressionClassification


class MathExpressionClassificationDocument(BaseModel):
    _id: str
    math_expression_id: str
    value: str

    @classmethod
    def from_internal(
        cls, inter: MathExpressionClassification
    ) -> 'MathExpressionClassificationDocument':
        return cls(
            _id=str(inter.id),
            math_expression_id=str(inter.math_expression_id),
            value=inter.value,
        )

    @classmethod
    def to_internal(
        cls, doc: 'MathExpressionClassificationDocument'
    ) -> MathExpressionClassification:
        return cls(
            id=UUID(doc._id),
            math_expression_id=UUID(doc.math_expression_id),
            value=doc.value,
        )
