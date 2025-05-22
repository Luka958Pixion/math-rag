from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionLabel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    index_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    math_expression_id: UUID
    value: MathExpressionLabelEnum
