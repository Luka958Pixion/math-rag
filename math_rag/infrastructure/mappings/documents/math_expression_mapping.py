from math_rag.core.models import MathExpression
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDocument


class MathExpressionMapping(BaseMapping[MathExpression, MathExpressionDocument]):
    @staticmethod
    def to_source(target: MathExpressionDocument) -> MathExpression:
        return MathExpression(
            id=target.id,
            math_article_id=target.math_article_id,
            math_expression_dataset_id=target.math_expression_dataset_id,
            math_expression_group_id=target.math_expression_group_id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
            latex=target.latex,
            katex=target.katex,
            index=target.index,
            position=target.position,
            is_inline=target.is_inline,
        )

    @staticmethod
    def to_target(source: MathExpression) -> MathExpressionDocument:
        return MathExpressionDocument(
            id=source.id,
            math_article_id=source.math_article_id,
            math_expression_dataset_id=source.math_expression_dataset_id,
            math_expression_group_id=source.math_expression_group_id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
            latex=source.latex,
            katex=source.katex,
            index=source.index,
            position=source.position,
            is_inline=source.is_inline,
        )
