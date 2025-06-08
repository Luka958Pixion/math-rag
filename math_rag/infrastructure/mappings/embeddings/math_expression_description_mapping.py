from datetime import datetime
from uuid import UUID

from math_rag.core.models import MathExpressionDescription
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.embeddings import MathExpressionDescriptionEmbedding


class MathExpressionDescriptionMapping(
    BaseMapping[MathExpressionDescription, MathExpressionDescriptionEmbedding]
):
    @staticmethod
    def to_source(target: MathExpressionDescriptionEmbedding) -> MathExpressionDescription:
        return MathExpressionDescription(
            id=UUID(target.id),
            math_expression_id=UUID(target.payload['math_expression_id']),
            index_id=target.payload['index_id'],
            timestamp=datetime.fromisoformat(target.payload['timestamp']),
            description=target.payload['description'],
        )

    @staticmethod
    def to_target(
        source: MathExpressionDescription, *, embedding: list[float]
    ) -> MathExpressionDescriptionEmbedding:
        return MathExpressionDescriptionEmbedding(
            id=str(source.id),
            vector=embedding,
            payload={
                'math_expression_id': str(source.math_expression_id),
                'index_id': source.index_id,
                'timestamp': source.timestamp.isoformat(),
                'description': source.description,
            },
        )
