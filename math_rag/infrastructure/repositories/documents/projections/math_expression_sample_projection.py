from math_rag.core.base import BaseSample


class MathExpressionSampleProjection(BaseSample):
    latex: str
    label: str
