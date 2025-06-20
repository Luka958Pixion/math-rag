from pydantic import BaseModel

from math_rag.core.models import MathExpressionDataset, Task


class Response(BaseModel):
    math_expression_dataset: MathExpressionDataset
    task: Task
