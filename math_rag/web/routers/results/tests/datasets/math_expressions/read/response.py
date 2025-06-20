from pydantic import BaseModel

from math_rag.core.models import MathExpressionDatasetTestResult


class Response(BaseModel):
    math_expression_dataset_test_result: MathExpressionDatasetTestResult
