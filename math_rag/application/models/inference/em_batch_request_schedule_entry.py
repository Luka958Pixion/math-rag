from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_batch_request import EMBatchRequest


class EMBatchRequestScheduleEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    batch_request: EMBatchRequest
    timestamp: datetime
