from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EMResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    embedding: list[float]
