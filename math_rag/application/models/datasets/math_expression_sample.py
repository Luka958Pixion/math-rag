from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpressionSample(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_id: UUID
    math_expression_label_id: UUID
    latex: str
    label: str
