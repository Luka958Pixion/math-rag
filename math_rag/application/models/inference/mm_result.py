from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .mm_failed_request import MMFailedRequest
from .mm_response_list import MMResponseList


class MMResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    response_list: MMResponseList
    failed_request: MMFailedRequest | None
