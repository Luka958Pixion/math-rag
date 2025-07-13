from math_rag.core.models import MathExpressionContext
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionContextDocument


class MathExpressionContextMapping(
    BaseMapping[MathExpressionContext, MathExpressionContextDocument]
):
    @staticmethod
    def to_source(
        target: MathExpressionContextDocument,
    ) -> MathExpressionContext:
        return MathExpressionContext(
            id=target.id,
            math_article_id=target.math_article_id,
            math_expression_id=target.math_expression_id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
            text=target.text,
        )

    @staticmethod
    def to_target(
        source: MathExpressionContext,
    ) -> MathExpressionContextDocument:
        return MathExpressionContextDocument(
            id=source.id,
            math_article_id=source.math_article_id,
            math_expression_id=source.math_expression_id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
            text=source.text,
        )
