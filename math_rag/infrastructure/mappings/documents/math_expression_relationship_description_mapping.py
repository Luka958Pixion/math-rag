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
        return MathExpressionRelationshipDescription.model_validate(target.model_dump())

    @staticmethod
    def to_target(
        source: MathExpressionRelationshipDescription,
    ) -> MathExpressionRelationshipDescriptionDocument:
        return MathExpressionRelationshipDescriptionDocument.model_validate(source.model_dump())
