from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import FineTuneJobRunStatus


class FineTuneJobCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    status: FineTuneJobRunStatus
    provider_name: str
    model_name: str
