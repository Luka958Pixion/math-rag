from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionGroupDocument(BaseDocument):
    id: UUID
    index_id: UUID | None
    timestamp: datetime
