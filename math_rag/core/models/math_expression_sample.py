from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionSample(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_dataset_id: UUID
    latex: str
    label: MathExpressionLabelEnum
