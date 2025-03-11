from math_rag.core.models import MathExpression
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDocument


class MathExpressionMapping(BaseMapping[MathExpression, MathExpressionDocument]):
    @staticmethod
    def to_source(target: MathExpressionDocument) -> MathExpression:
        return MathExpression(
            id=target.id,
            latex=target.latex,
            katex=target.katex,
            position=target.position,
            is_inline=target.is_inline,
        )

    @staticmethod
    def to_target(source: MathExpression) -> MathExpressionDocument:
        return MathExpressionDocument(
            id=source.id,
            latex=source.latex,
            katex=source.katex,
            position=source.position,
            is_inline=source.is_inline,
        )
