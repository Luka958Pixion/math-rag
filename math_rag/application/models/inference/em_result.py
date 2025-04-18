from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_failed_request import EMFailedRequest
from .em_response_list import EMResponseList


class EMResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    response_list: EMResponseList
    failed_request: EMFailedRequest | None
