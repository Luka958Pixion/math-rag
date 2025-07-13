from uuid import UUID

from math_rag.core.models import MathExpressionRelationship
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.graphs import MathExpressionRel


class MathExpressionRelationshipMapping(BaseMapping[MathExpressionRelationship, MathExpressionRel]):
    @staticmethod
    def to_source(target: MathExpressionRel) -> MathExpressionRelationship:
        return MathExpressionRelationship(
            id=UUID(target.uid),
            math_article_chunk_id=UUID(target.math_article_chunk_id),
            math_expression_index_id=UUID(target.math_expression_index_id),
            math_expression_source_id=UUID(target.math_expression_source_id),
            math_expression_target_id=UUID(target.math_expression_target_id),
            math_expression_source_index=target.math_expression_source_index,
            math_expression_target_index=target.math_expression_target_index,
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(source: MathExpressionRelationship) -> MathExpressionRel:
        return MathExpressionRel(
            uid=str(source.id),
            math_article_chunk_id=str(source.math_article_chunk_id),
            math_expression_index_id=str(source.math_expression_index_id),
            math_expression_source_id=str(source.math_expression_source_id),
            math_expression_target_id=str(source.math_expression_target_id),
            math_expression_source_index=source.math_expression_source_index,
            math_expression_target_index=source.math_expression_target_index,
            timestamp=source.timestamp,
        )
