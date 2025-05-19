from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_article_id: UUID
    latex: str
    katex: str | None
    position: int
    is_inline: bool
