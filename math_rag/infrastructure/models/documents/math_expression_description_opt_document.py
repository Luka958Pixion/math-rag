from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDescriptionOptDocument(BaseDocument):
    id: UUID
    math_expression_id: UUID
    math_expression_description_id: UUID
    math_expression_index_id: UUID
    timestamp: datetime
    description: str
