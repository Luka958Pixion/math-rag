from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionRelationshipDocument(BaseDocument):
    id: UUID
    math_expression_index_id: UUID
    math_expression_source_id: UUID
    math_expression_target_id: UUID
    timestamp: datetime
