from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionLabelDocument(BaseDocument):
    id: UUID
    math_expression_id: UUID
    math_expression_dataset_id: UUID | None
    index_id: UUID | None
    timestamp: datetime
    value: str
