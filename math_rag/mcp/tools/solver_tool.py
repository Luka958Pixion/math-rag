from asyncio import sleep
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from math_rag.application.base.repositories.documents import (
    BaseMathProblemRepository,
    BaseMathProblemSolutionRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.enums import TaskStatus
from math_rag.core.models import MathProblem, Task
from math_rag.mcp.base import BaseTool


POLL_INTERVAL = 15


class SolverToolResult(BaseModel):
    solution: str


class SolverTool(BaseTool):
    async def solve(
        self,
        image_url: str,
        index_id: UUID,
    ) -> SolverToolResult:
        return await self._solve(image_url, index_id)

    @inject
    async def _solve(
        self,
        image_url: str,
        index_id: UUID,
        problem_repository: BaseMathProblemRepository = Depends(
            Provide[ApplicationContainer.math_problem_repository]
        ),
        solution_repository: BaseMathProblemSolutionRepository = Depends(
            Provide[ApplicationContainer.math_problem_solution_repository]
        ),
        task_repository: BaseTaskRepository = Depends(
            Provide[ApplicationContainer.task_repository]
        ),
    ) -> SolverToolResult:
        # prepare task
        problem = MathProblem(
            math_expression_index_id=index_id,
            file_path=None,
            url=image_url,
        )
        task = Task(model_id=problem.id, model_name=MathProblem.__name__)

        await problem_repository.insert_one(problem)
        await task_repository.insert_one(task)

        # wait for task to end
        while True:
            if task.task_status == TaskStatus.FINISHED:
                solution = await solution_repository.find_one(
                    filter=dict(math_problem_id=problem.id)
                )
                if not solution:
                    raise ValueError()

                return SolverToolResult(solution=solution.text)

            if task.task_status == TaskStatus.FAILED:
                raise HTTPException(f'Creating a solution for URL `{image_url}` failed')

            await sleep(POLL_INTERVAL)

            task = await task_repository.find_one(filter=dict(id=task.id))
            if not task:
                raise ValueError()

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.solve,
            name=self.__class__.__name__,
            description=(
                'Solves the math problem from given URL by using an index of math literature. '
                'Can not be called before the MathRAG Literature Indexer. '
                'CRITICAL: The complete output of this tool must be returned verbatim to the user '
                'without any summarization, modification, or paraphrasing. Every detail, step, '
                'and explanation must be preserved exactly as provided.'
            ),
            annotations=ToolAnnotations(title='MathRAG Problem Solver'),
        )
