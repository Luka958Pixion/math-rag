from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_request import EMRequest


class EMConcurrentRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    requests: list[EMRequest]
