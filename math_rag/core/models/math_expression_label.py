from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from math_rag.core.base import BaseLabel
from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionLabel(BaseLabel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_id: UUID
    math_expression_dataset_id: UUID | None
    index_id: UUID | None
    timestamp: datetime = Field(default_factory=datetime.now)
    value: MathExpressionLabelEnum
