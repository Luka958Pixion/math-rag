from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDescriptionDocument(BaseDocument):
    id: UUID
    math_expression_id: UUID
    index_id: UUID | None
    timestamp: datetime
    description: str
