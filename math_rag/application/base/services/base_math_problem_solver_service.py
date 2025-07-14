from abc import ABC, abstractmethod

from math_rag.core.models import MathProblem, MathProblemSolution


class BaseMathProblemSolverService(ABC):
    @abstractmethod
    async def solve(self, math_problem: MathProblem) -> MathProblemSolution:
        pass
