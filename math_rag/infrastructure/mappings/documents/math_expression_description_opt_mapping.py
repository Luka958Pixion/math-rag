from math_rag.core.models import MathExpressionDescriptionOpt
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDescriptionOptDocument


class MathExpressionDescriptionOptMapping(
    BaseMapping[MathExpressionDescriptionOpt, MathExpressionDescriptionOptDocument]
):
    @staticmethod
    def to_source(
        target: MathExpressionDescriptionOptDocument,
    ) -> MathExpressionDescriptionOpt:
        return MathExpressionDescriptionOpt(
            id=target.id,
            math_expression_id=target.math_expression_id,
            math_expression_description_id=target.math_expression_description_id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
            text=target.text,
        )

    @staticmethod
    def to_target(
        source: MathExpressionDescriptionOpt,
    ) -> MathExpressionDescriptionOptDocument:
        return MathExpressionDescriptionOptDocument(
            id=source.id,
            math_expression_id=source.math_expression_id,
            math_expression_description_id=source.math_expression_description_id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
            text=source.text,
        )
