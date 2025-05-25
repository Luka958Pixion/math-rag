from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class IndexDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    build_stage: str
    build_status: str
    build_from_index_id: UUID | None
    build_from_stage: str | None
