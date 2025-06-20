from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .math_expression_label import MathExpressionLabel


class MathExpressionDatasetTestResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_dataset_id: UUID
    math_expression_dataset_test_id: UUID
    math_expression_labels: list[MathExpressionLabel]
    timestamp: datetime = Field(default_factory=datetime.now)
