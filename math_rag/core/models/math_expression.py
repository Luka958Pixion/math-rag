from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    latex: str
    katex: str | None
    position: int
    is_inline: bool
