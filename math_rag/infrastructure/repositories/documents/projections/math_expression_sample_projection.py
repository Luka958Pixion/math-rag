from uuid import UUID

from math_rag.core.base import BaseSample


class MathExpressionSampleProjection(BaseSample):
    math_expression_id: UUID
    katex: str
    label: str
