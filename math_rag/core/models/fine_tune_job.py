from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import TaskStatus


class FineTuneJob(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    task_status: TaskStatus = Field(default=TaskStatus.PENDING)
    provider_name: str
    model_name: str
