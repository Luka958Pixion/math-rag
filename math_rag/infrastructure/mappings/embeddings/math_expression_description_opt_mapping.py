from datetime import datetime
from uuid import UUID

from math_rag.core.models import MathExpressionDescriptionOpt
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.embeddings import (
    MathExpressionDescriptionOptEmbedding,
)


class MathExpressionDescriptionOptMapping(
    BaseMapping[MathExpressionDescriptionOpt, MathExpressionDescriptionOptEmbedding]
):
    @staticmethod
    def to_source(
        target: MathExpressionDescriptionOptEmbedding,
    ) -> MathExpressionDescriptionOpt:
        return MathExpressionDescriptionOpt(
            id=UUID(target.id),
            math_expression_id=UUID(target.payload['math_expression_id']),
            math_expression_description_id=UUID(target.payload['math_expression_description_id']),
            math_expression_index_id=target.payload['math_expression_index_id'],
            timestamp=datetime.fromisoformat(target.payload['timestamp']),
            text=target.payload['text'],
        )

    @staticmethod
    def to_target(
        source: MathExpressionDescriptionOpt, *, embedding: list[float]
    ) -> MathExpressionDescriptionOptEmbedding:
        return MathExpressionDescriptionOptEmbedding(
            id=str(source.id),
            vector=embedding,
            payload={
                'math_expression_id': str(source.math_expression_id),
                'math_expression_description_id': str(source.math_expression_description_id),
                'math_expression_index_id': source.math_expression_index_id,
                'timestamp': source.timestamp.isoformat(),
                'text': source.text,
            },
        )
