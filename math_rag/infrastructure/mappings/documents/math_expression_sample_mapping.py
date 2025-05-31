from math_rag.core.models import MathExpressionSample
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionSampleDocument


class MathExpressionSampleMapping(BaseMapping[MathExpressionSample, MathExpressionSampleDocument]):
    @staticmethod
    def to_source(target: MathExpressionSampleDocument) -> MathExpressionSample:
        return MathExpressionSample(
            id=target.id,
            math_expression_dataset_id=target.math_expression_dataset_id,
            timestamp=target.timestamp,
            latex=target.latex,
        )

    @staticmethod
    def to_target(source: MathExpressionSample) -> MathExpressionSampleDocument:
        return MathExpressionSampleDocument(
            id=source.id,
            math_expression_dataset_id=source.math_expression_dataset_id,
            timestamp=source.timestamp,
            latex=source.latex,
        )
