from uuid import UUID

from pydantic import BaseModel


class HelperJob(BaseModel):
    fine_tune_job_id: UUID
    timestamp: int
