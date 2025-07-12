from uuid import UUID

from math_rag.core.models import MathExpression
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.graphs import MathExpressionNode


class MathExpressionMapping(BaseMapping[MathExpression, MathExpressionNode]):
    @staticmethod
    def to_source(target: MathExpressionNode) -> MathExpression:
        return MathExpression(
            id=UUID(target.uid),
            math_article_id=UUID(target.math_article_id),
            math_expression_dataset_id=UUID(target.math_expression_dataset_id)
            if target.math_expression_dataset_id
            else None,
            math_expression_group_id=UUID(target.math_expression_group_id)
            if target.math_expression_group_id
            else None,
            math_expression_index_id=UUID(target.math_expression_index_id)
            if target.math_expression_index_id
            else None,
            timestamp=target.timestamp,
            latex=target.latex,
            katex=target.katex,
            position=target.position,
            is_inline=target.is_inline,
        )

    @staticmethod
    def to_target(source: MathExpression) -> MathExpressionNode:
        return MathExpressionNode(
            uid=str(source.id),
            math_article_id=str(source.math_article_id),
            math_expression_dataset_id=str(source.math_expression_dataset_id)
            if source.math_expression_dataset_id
            else None,
            math_expression_group_id=str(source.math_expression_group_id)
            if source.math_expression_group_id
            else None,
            math_expression_index_id=str(source.math_expression_index_id)
            if source.math_expression_index_id
            else None,
            timestamp=source.timestamp,
            latex=source.latex,
            katex=source.katex,
            position=source.position,
            is_inline=source.is_inline,
        )
