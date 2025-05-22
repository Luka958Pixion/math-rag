from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionLabelDocument(BaseDocument):
    id: UUID
    index_id: UUID
    timestamp: datetime
    math_expression_id: UUID
    value: str
