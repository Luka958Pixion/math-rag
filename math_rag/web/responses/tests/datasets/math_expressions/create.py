from pydantic import BaseModel

from math_rag.core.models import MathExpressionDatasetTest, Task


class MathExpressionDatasetTestCreateResponse(BaseModel):
    math_expression_dataset_test: MathExpressionDatasetTest
    task: Task
