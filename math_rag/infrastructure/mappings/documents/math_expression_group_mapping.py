from math_rag.core.models import MathExpressionGroup
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionGroupDocument


class MathExpressionGroupMapping(BaseMapping[MathExpressionGroup, MathExpressionGroupDocument]):
    @staticmethod
    def to_source(target: MathExpressionGroupDocument) -> MathExpressionGroup:
        return MathExpressionGroup.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: MathExpressionGroup) -> MathExpressionGroupDocument:
        return MathExpressionGroupDocument.model_validate(source.model_dump())
