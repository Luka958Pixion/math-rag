from math_rag.core.models import MathExpressionDescriptionOpt
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDescriptionOptDocument


class MathExpressionDescriptionOptMapping(
    BaseMapping[MathExpressionDescriptionOpt, MathExpressionDescriptionOptDocument]
):
    @staticmethod
    def to_source(target: MathExpressionDescriptionOptDocument) -> MathExpressionDescriptionOpt:
        return MathExpressionDescriptionOpt.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: MathExpressionDescriptionOpt) -> MathExpressionDescriptionOptDocument:
        return MathExpressionDescriptionOptDocument.model_validate(source.model_dump())
