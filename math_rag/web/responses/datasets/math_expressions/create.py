from pydantic import BaseModel

from math_rag.core.models import MathExpressionDataset, Task


class MathExpressionDatasetCreateResponse(BaseModel):
    math_expression_dataset: MathExpressionDataset
    task: Task
