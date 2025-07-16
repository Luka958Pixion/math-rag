from uuid import UUID

from math_rag.application.base.repositories.documents import (
    BaseMathProblemRepository,
    BaseMathProblemSolutionRepository,
    BaseTaskRepository,
)
from math_rag.application.base.services import BaseMathProblemSolverService
from math_rag.core.models import MathProblem

from .partials import PartialTaskBackgroundService


class MathProblemBackgroundService(PartialTaskBackgroundService):
    def __init__(
        self,
        math_problem_solver_service: BaseMathProblemSolverService,
        math_problem_repository: BaseMathProblemRepository,
        math_problem_solution_repository: BaseMathProblemSolutionRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.math_problem_solver_service = math_problem_solver_service
        self.math_problem_repository = math_problem_repository
        self.math_problem_solution_repository = math_problem_solution_repository

    async def task(self, task_model_id: UUID):
        problem = await self.math_problem_repository.find_one(filter=dict(id=task_model_id))

        if not problem:
            raise ValueError()

        solution = await self.math_problem_solver_service.solve(problem)
        await self.math_problem_solution_repository.insert_one(solution)

    def task_model_name(self) -> str:
        return MathProblem.__name__
