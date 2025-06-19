from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class FineTuneJobDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    task_status: str
    provider_name: str
    model_name: str
