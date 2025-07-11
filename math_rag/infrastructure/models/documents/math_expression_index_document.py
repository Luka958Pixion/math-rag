from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionIndexDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    build_stage: str
