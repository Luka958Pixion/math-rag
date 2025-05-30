from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class DatasetDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    build_stage: str
    build_status: str
    build_from_dataset_id: UUID | None
    build_from_stage: str | None
