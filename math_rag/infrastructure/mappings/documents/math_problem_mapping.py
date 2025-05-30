from math_rag.core.models import MathProblem
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathProblemDocument


class MathProblemMapping(BaseMapping[MathProblem, MathProblemDocument]):
    @staticmethod
    def to_source(target: MathProblemDocument) -> MathProblem:
        return MathProblem(
            id=target.id,
            timestamp=target.timestamp,
            latex=target.latex,
            katex=target.katex,
            is_inline=target.is_inline,
        )

    @staticmethod
    def to_target(source: MathProblem) -> MathProblemDocument:
        return MathProblemDocument(
            id=source.id,
            timestamp=source.timestamp,
            latex=source.latex,
            katex=source.katex,
            is_inline=source.is_inline,
        )
