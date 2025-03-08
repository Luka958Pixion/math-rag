from uuid import UUID

from pydantic import BaseModel


class MathExpressionDocument(BaseModel):
    _id: UUID
    latex: str
    katex: str | None
    position: int
    is_inline: bool
