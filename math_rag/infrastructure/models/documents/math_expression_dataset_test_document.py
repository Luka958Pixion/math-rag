from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDatasetTestDocument(BaseDocument):
    id: UUID
    math_expression_dataset_id: UUID
    math_expression_dataset_split_name: str
    timestamp: datetime
    inference_provider: str
    model_provider: str
    model: str
