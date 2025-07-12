from math_rag.core.models import MathExpressionContext
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionContextDocument


class MathExpressionContextMapping(
    BaseMapping[MathExpressionContext, MathExpressionContextDocument]
):
    @staticmethod
    def to_source(
        target: MathExpressionContextDocument,
    ) -> MathExpressionContext:
        return MathExpressionContext.model_validate(target.model_dump())

    @staticmethod
    def to_target(
        source: MathExpressionContext,
    ) -> MathExpressionContextDocument:
        return MathExpressionContextDocument.model_validate(source.model_dump())
