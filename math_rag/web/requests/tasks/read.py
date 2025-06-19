from uuid import UUID

from pydantic import BaseModel


class TaskReadRequest(BaseModel):
    task_id: UUID
