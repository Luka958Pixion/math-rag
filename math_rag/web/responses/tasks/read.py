from pydantic import BaseModel

from math_rag.core.models import Task


class TaskReadResponse(BaseModel):
    task: Task | None
