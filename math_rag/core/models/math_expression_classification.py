from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpressionClassification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_id: UUID
    value: str
