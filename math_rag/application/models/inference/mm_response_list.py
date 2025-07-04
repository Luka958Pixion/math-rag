from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .mm_response import MMResponse


class MMResponseList(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    responses: list[MMResponse]
