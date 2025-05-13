from uuid import UUID

from math_rag.application.base.datasets import BaseSample


class MathExpressionSample(BaseSample):
    latex: str
    label: str
