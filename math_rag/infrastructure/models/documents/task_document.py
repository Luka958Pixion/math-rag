from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class TaskDocument(BaseDocument):
    id: UUID
    model_id: UUID
    model_name: str
    created_at: datetime
    started_at: datetime | None
    failed_at: datetime | None
    finished_at: datetime | None
    task_status: str
