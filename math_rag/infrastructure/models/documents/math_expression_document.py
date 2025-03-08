from uuid import UUID

from pydantic import BaseModel

from math_rag.core.models import MathExpression


class MathExpressionDocument(BaseModel):
    _id: str
    latex: str
    katex: str | None
    position: int
    is_inline: bool

    @classmethod
    def from_internal(cls, inter: MathExpression) -> 'MathExpressionDocument':
        return cls(
            _id=str(inter.id),
            latex=inter.latex,
            katex=inter.katex,
            position=inter.position,
            is_inline=inter.is_inline,
        )

    @classmethod
    def to_internal(cls, doc: 'MathExpressionDocument') -> MathExpression:
        return cls(
            id=UUID(doc._id),
            latex=doc.latex,
            katex=doc.katex,
            position=doc.position,
            is_inline=doc.is_inline,
        )
