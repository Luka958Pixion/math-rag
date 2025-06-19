from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import TaskStatus


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    model_type: str
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime = Field(default_factory=datetime.now)
    failed_at: datetime = Field(default_factory=datetime.now)
    finished_at: datetime = Field(default_factory=datetime.now)
    task_status: TaskStatus = Field(default=TaskStatus.PENDING)
