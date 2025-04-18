from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_error import EMError
from .em_request import EMRequest


class EMFailedRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request: EMRequest
    errors: list[EMError]
