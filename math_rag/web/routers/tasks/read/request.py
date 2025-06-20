from uuid import UUID

from pydantic import BaseModel


class Request(BaseModel):
    task_id: UUID
