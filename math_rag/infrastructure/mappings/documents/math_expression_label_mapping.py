from math_rag.core.models import MathExpressionLabel
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionLabelDocument


class MathExpressionLabelMapping(BaseMapping[MathExpressionLabel, MathExpressionLabelDocument]):
    @staticmethod
    def to_source(
        target: MathExpressionLabelDocument,
    ) -> MathExpressionLabel:
        return MathExpressionLabel(
            id=target.id,
            math_expression_id=target.math_expression_id,
            dataset_id=target.dataset_id,
            index_id=target.index_id,
            timestamp=target.timestamp,
            value=target.value,
        )

    @staticmethod
    def to_target(
        source: MathExpressionLabel,
    ) -> MathExpressionLabelDocument:
        return MathExpressionLabelDocument(
            id=source.id,
            math_expression_id=source.math_expression_id,
            dataset_id=source.dataset_id,
            index_id=source.index_id,
            timestamp=source.timestamp,
            value=source.value,
        )
