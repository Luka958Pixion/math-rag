from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionSampleDocument(BaseDocument):
    id: UUID
    math_expression_dataset_id: UUID
    timestamp: datetime
    latex: str
    label: str
