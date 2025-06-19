from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class IndexDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    build_stage: str
    task_status: str
