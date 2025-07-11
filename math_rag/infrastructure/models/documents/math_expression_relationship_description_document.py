from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionRelationshipDescriptionDocument(BaseDocument):
    id: UUID
    math_expression_index_id: UUID
    math_expression_relationship_id: UUID
    timestamp: datetime
    description: str
