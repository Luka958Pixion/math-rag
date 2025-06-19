from pydantic import BaseModel

from math_rag.core.models import MathExpressionLabel


class MathExpressionDatasetTestCreateResponse(BaseModel):
    labels: list[MathExpressionLabel]
