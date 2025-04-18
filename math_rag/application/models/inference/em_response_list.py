from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_response import EMResponse


class EMResponseList(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    responses: list[EMResponse]
