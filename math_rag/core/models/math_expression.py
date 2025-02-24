from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import MathCategory


class MathExpression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    latex: str
    position: int
    is_inline: bool
    math_category: MathCategory
