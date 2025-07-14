from math_rag.application.base.services import BaseMathProblemSolverService
from math_rag.core.models import MathProblem, MathProblemSolution


class MathProblemSolverService(BaseMathProblemSolverService):
    def __init__(self):
        pass

    async def solve(self, math_problem: MathProblem) -> MathProblemSolution:
        pass
