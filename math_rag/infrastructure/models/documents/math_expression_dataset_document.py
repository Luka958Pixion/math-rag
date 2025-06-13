from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDatasetDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    build_stage: str
    build_status: str
    build_from_id: UUID | None
    build_from_stage: str | None
    build_priority: str
    # NOTE: samples don't go here because they would exceed the document size limit
