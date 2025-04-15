from uuid import UUID

from pydantic import BaseModel


class BatchJobRequest(BaseModel):
    source_batch_request_id: UUID
    target_pbs_job_id: str
