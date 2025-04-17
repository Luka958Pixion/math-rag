from uuid import UUID

from pydantic import BaseModel


class BatchJob(BaseModel):
    batch_request_id: UUID
    model_hub_id: str
