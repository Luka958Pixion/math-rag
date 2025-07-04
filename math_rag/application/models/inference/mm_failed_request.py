from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .mm_error import MMError
from .mm_request import MMRequest


class MMFailedRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request: MMRequest
    errors: list[MMError]
