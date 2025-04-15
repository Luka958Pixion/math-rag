from uuid import UUID

from pydantic import BaseModel


class BatchJobResponse(BaseModel):
    batch_request_id: UUID
    pbs_job_id: str
    allowed: bool
