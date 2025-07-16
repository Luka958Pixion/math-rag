from pydantic import BaseModel

from math_rag.core.models import MathProblem, Task


class Response(BaseModel):
    math_problem: MathProblem
    task: Task
