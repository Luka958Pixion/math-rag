from math_rag.application.models.datasets import MathExpressionSample
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.views import (
    MathExpressionSampleDocumentView,
)


class MathExpressionSampleMapping(
    BaseMapping[MathExpressionSample, MathExpressionSampleDocumentView]
):
    @staticmethod
    def to_source(target: MathExpressionSampleDocumentView) -> MathExpressionSample:
        return MathExpressionSample(label=target.label, latex=target.latex)

    @staticmethod
    def to_target(source: MathExpressionSample) -> MathExpressionSampleDocumentView:
        return MathExpressionSampleDocumentView(label=source.label, latex=source.latex)
