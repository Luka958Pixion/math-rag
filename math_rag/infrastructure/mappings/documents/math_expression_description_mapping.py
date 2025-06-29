from math_rag.core.models import MathExpressionDescription
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDescriptionDocument


class MathExpressionDescriptionMapping(
    BaseMapping[MathExpressionDescription, MathExpressionDescriptionDocument]
):
    @staticmethod
    def to_source(target: MathExpressionDescriptionDocument) -> MathExpressionDescription:
        return MathExpressionDescription.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: MathExpressionDescription) -> MathExpressionDescriptionDocument:
        return MathExpressionDescriptionDocument.model_validate(source.model_dump())
