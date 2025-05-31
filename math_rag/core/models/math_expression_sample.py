from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from math_rag.core.base import BaseSample
from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionSample(BaseSample):
    id: UUID = Field(default_factory=uuid4)
    math_expression_dataset_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    latex: str
    label: MathExpressionLabelEnum
