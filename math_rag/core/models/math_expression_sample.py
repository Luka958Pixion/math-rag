from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field, field_validator

from math_rag.core.base import BaseSample
from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionSample(BaseSample):
    id: UUID = Field(default_factory=uuid4)
    math_expression_dataset_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    latex: str
    label: MathExpressionLabelEnum

    @field_validator('label', mode='before')
    def coerce_int_to_label(cls, value):
        if isinstance(value, int):
            return MathExpressionLabelEnum.from_index(value)

        return value
