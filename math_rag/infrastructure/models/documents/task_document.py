from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class TaskDocument(BaseDocument):
    id: UUID
    model_id: UUID
    created_at: datetime
    started_at: datetime
    failed_at: datetime
    finished_at: datetime
    task_status: str
