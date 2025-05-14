from math_rag.application.base.datasets import BaseSample
from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionSample(BaseSample):
    latex: str
    label: MathExpressionLabelEnum
