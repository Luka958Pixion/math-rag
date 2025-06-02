from uuid import UUID

from pydantic import BaseModel

from math_rag.infrastructure.enums.fine_tune.huggingface import HelperJobStatus


class HelperJobStatusTracker(BaseModel):
    is_status_update_allowed: bool
    id_to_status: dict[UUID, HelperJobStatus]
