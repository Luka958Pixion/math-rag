from math_rag.core.models import MathExpressionDescription
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.embeddings import MathExpressionDescriptionEmbedding


class MathExpressionDescriptionMapping(
    BaseMapping[MathExpressionDescription, MathExpressionDescriptionEmbedding]
):
    @staticmethod
    def to_source(target: MathExpressionDescriptionEmbedding) -> MathExpressionDescription:
        return MathExpressionDescription(  # TODO
            id=target.id,
            math_expression_id=target.math_expression_id,
            index_id=target.index_id,
            timestamp=target.timestamp,
            description=target.description,
        )

    @staticmethod
    def to_target(source: MathExpressionDescription) -> MathExpressionDescriptionEmbedding:
        # TODO vector??
        return MathExpressionDescriptionEmbedding(
            id=str(source.id),
            vector=...,
            payload=...,  # TODO
        )
