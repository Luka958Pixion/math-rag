from uuid import UUID

from pydantic import BaseModel


class MathExpressionSample(BaseModel):
    math_expression_id: UUID
    math_expression_label_id: UUID
    latex: str
    label: str
