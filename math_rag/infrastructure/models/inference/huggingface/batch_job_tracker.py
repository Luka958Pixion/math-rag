from uuid import UUID

from pydantic import BaseModel

from math_rag.infrastructure.enums.inference.huggingface import BatchJobStatus


class BatchJobStatusTracker(BaseModel):
    is_status_update_allowed: bool
    id_to_status: dict[UUID, BatchJobStatus]
