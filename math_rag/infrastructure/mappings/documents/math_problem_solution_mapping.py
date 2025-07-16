from math_rag.core.models import MathProblemSolution
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathProblemSolutionDocument


class MathProblemSolutionMapping(BaseMapping[MathProblemSolution, MathProblemSolutionDocument]):
    @staticmethod
    def to_source(target: MathProblemSolutionDocument) -> MathProblemSolution:
        return MathProblemSolution(
            id=target.id,
            math_problem_id=target.math_problem_id,
            timestamp=target.timestamp,
            text=target.text,
        )

    @staticmethod
    def to_target(source: MathProblemSolution) -> MathProblemSolutionDocument:
        return MathProblemSolutionDocument(
            id=source.id,
            math_problem_id=source.math_problem_id,
            timestamp=source.timestamp,
            text=source.text,
        )
