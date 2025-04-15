from uuid import UUID

from pydantic import BaseModel


class BatchJobRequest(BaseModel):
    batch_request_id: UUID
    pbs_job_id: str
