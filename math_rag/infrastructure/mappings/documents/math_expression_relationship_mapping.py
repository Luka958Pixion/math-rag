from math_rag.core.models import MathExpressionRelationship
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionRelationshipDocument


class MathExpressionRelationshipMapping(
    BaseMapping[MathExpressionRelationship, MathExpressionRelationshipDocument]
):
    @staticmethod
    def to_source(target: MathExpressionRelationshipDocument) -> MathExpressionRelationship:
        return MathExpressionRelationship(
            id=target.id,
            math_article_chunk_id=target.math_article_chunk_id,
            math_expression_index_id=target.math_expression_index_id,
            math_expression_source_id=target.math_expression_source_id,
            math_expression_target_id=target.math_expression_target_id,
            math_expression_source_index=target.math_expression_source_index,
            math_expression_target_index=target.math_expression_target_index,
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(source: MathExpressionRelationship) -> MathExpressionRelationshipDocument:
        return MathExpressionRelationshipDocument(
            id=source.id,
            math_article_chunk_id=source.math_article_chunk_id,
            math_expression_index_id=source.math_expression_index_id,
            math_expression_source_id=source.math_expression_source_id,
            math_expression_target_id=source.math_expression_target_id,
            math_expression_source_index=source.math_expression_source_index,
            math_expression_target_index=source.math_expression_target_index,
            timestamp=source.timestamp,
        )
