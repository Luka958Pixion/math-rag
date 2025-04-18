from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_failed_request import EMFailedRequest
from .em_response_list import EMResponseList


class EMBatchResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    batch_request_id: UUID
    response_lists: list[EMResponseList]
    failed_requests: list[EMFailedRequest]
