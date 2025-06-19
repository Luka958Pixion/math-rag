from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import TaskStatus


class FineTuneJobCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    task_status: TaskStatus
    provider_name: str
    model_name: str
