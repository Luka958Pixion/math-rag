from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpressionDatasetTest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_dataset_id: UUID
    math_expression_dataset_split_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    inference_provider: str
    model_provider: str
    model: str
