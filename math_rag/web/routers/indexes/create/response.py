from pydantic import BaseModel

from math_rag.core.models import MathExpressionIndex, Task


class Response(BaseModel):
    index: MathExpressionIndex
    task: Task
