from math_rag.core.models import MathProblem
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathProblemDocument


class MathProblemMapping(BaseMapping[MathProblem, MathProblemDocument]):
    @staticmethod
    def to_source(target: MathProblemDocument) -> MathProblem:
        return MathProblem(
            id=target.id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
            latex=target.latex,
        )

    @staticmethod
    def to_target(source: MathProblem) -> MathProblemDocument:
        return MathProblemDocument(
            id=source.id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
            latex=source.latex,
        )
