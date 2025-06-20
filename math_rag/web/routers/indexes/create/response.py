from pydantic import BaseModel

from math_rag.core.models import Index, Task


class Response(BaseModel):
    index: Index
    task: Task
