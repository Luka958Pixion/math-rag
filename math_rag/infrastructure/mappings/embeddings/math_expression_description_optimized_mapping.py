from datetime import datetime
from uuid import UUID

from math_rag.core.models import MathExpressionDescriptionOptimized
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.embeddings import (
    MathExpressionDescriptionOptimizedEmbedding,
)


class MathExpressionDescriptionOptimizedMapping(
    BaseMapping[MathExpressionDescriptionOptimized, MathExpressionDescriptionOptimizedEmbedding]
):
    @staticmethod
    def to_source(
        target: MathExpressionDescriptionOptimizedEmbedding,
    ) -> MathExpressionDescriptionOptimized:
        return MathExpressionDescriptionOptimized(
            id=UUID(target.id),
            math_expression_id=UUID(target.payload['math_expression_id']),
            math_expression_description_id=UUID(target.payload['math_expression_description_id']),
            index_id=target.payload['index_id'],
            timestamp=datetime.fromisoformat(target.payload['timestamp']),
            description=target.payload['description'],
        )

    @staticmethod
    def to_target(
        source: MathExpressionDescriptionOptimized, *, embedding: list[float]
    ) -> MathExpressionDescriptionOptimizedEmbedding:
        return MathExpressionDescriptionOptimizedEmbedding(
            id=str(source.id),
            vector=embedding,
            payload={
                'math_expression_id': str(source.math_expression_id),
                'math_expression_description_id': str(source.math_expression_description_id),
                'index_id': source.index_id,
                'timestamp': source.timestamp.isoformat(),
                'description': source.description,
            },
        )
