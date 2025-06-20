from pydantic import BaseModel

from math_rag.core.models import Task


class Response(BaseModel):
    task: Task
