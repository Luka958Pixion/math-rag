from uuid import UUID

from pydantic import BaseModel


class BatchJobResponse(BaseModel):
    source_pbs_job_id: str
    target_batch_request_id: UUID
    allowed: bool
