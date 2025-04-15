from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EMBatchResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    batch_request_id: UUID
    embeddings: list[list[float]]
