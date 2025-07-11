from math_rag.core.models import MathExpressionRelationship
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionRelationshipDocument


class MathExpressionRelationshipMapping(
    BaseMapping[MathExpressionRelationship, MathExpressionRelationshipDocument]
):
    @staticmethod
    def to_source(target: MathExpressionRelationshipDocument) -> MathExpressionRelationship:
        return MathExpressionRelationship.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: MathExpressionRelationship) -> MathExpressionRelationshipDocument:
        return MathExpressionRelationshipDocument.model_validate(source.model_dump())
