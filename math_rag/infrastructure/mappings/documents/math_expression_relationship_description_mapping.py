from math_rag.core.models import MathExpressionRelationshipDescription
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionRelationshipDescriptionDocument


class MathExpressionRelationshipDescriptionMapping(
    BaseMapping[
        MathExpressionRelationshipDescription, MathExpressionRelationshipDescriptionDocument
    ]
):
    @staticmethod
    def to_source(
        target: MathExpressionRelationshipDescriptionDocument,
    ) -> MathExpressionRelationshipDescription:
        return MathExpressionRelationshipDescription(
            id=target.id,
            math_expression_index_id=target.math_expression_index_id,
            math_expression_relationship_id=target.math_expression_relationship_id,
            timestamp=target.timestamp,
            text=target.text,
        )

    @staticmethod
    def to_target(
        source: MathExpressionRelationshipDescription,
    ) -> MathExpressionRelationshipDescriptionDocument:
        return MathExpressionRelationshipDescriptionDocument(
            id=source.id,
            math_expression_index_id=source.math_expression_index_id,
            math_expression_relationship_id=source.math_expression_relationship_id,
            timestamp=source.timestamp,
            text=source.text,
        )
