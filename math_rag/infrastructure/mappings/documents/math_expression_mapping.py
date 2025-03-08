from math_rag.core.models import MathExpression
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDocument


class MathExpressionMapping(BaseMapping[MathExpression, MathExpressionDocument]):
    @classmethod
    def to_source(cls, target: MathExpressionDocument) -> MathExpression:
        return cls(
            id=target._id,
            latex=target.latex,
            katex=target.katex,
            position=target.position,
            is_inline=target.is_inline,
        )

    @classmethod
    def to_target(cls, source: MathExpression) -> MathExpressionDocument:
        return cls(
            _id=source.id,
            latex=source.latex,
            katex=source.katex,
            position=source.position,
            is_inline=source.is_inline,
        )
