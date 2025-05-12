from uuid import UUID

from math_rag.application.base.datasets import BaseSample


class MathExpressionSample(BaseSample):
    math_expression_id: UUID
    math_expression_label_id: UUID
    latex: str
    label: str
