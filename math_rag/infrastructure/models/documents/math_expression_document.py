from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDocument(BaseDocument):
    id: UUID
    latex: str
    katex: str | None
    position: int
    is_inline: bool
