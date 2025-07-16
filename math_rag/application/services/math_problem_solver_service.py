from agents import Runner

from math_rag.application.agents import (
    KATEX_VALIDATOR_INPUT_TEMPLATE,
    MATH_PROBLEM_SOLVER_INPUT_TEMPLATE,
    KatexValidatorAgent,
    MathProblemSolverAgent,
)
from math_rag.application.base.clients import BaseJupyterClient
from math_rag.application.base.services import BaseMathProblemSolverService
from math_rag.core.models import MathProblem, MathProblemSolution


class MathProblemSolverService(BaseMathProblemSolverService):
    def __init__(self, jupyter_client: BaseJupyterClient):
        self.jupyter_client = jupyter_client

    async def solve(self, math_problem: MathProblem) -> MathProblemSolution:
        try:
            await self.jupyter_client.start_session(user_id='0')

            math_problem_solver_agent = MathProblemSolverAgent(
                math_problem.math_expression_index_id
            )
            katex_validator_agent = KatexValidatorAgent()

            solver_result = await Runner.run(
                math_problem_solver_agent,
                input=MATH_PROBLEM_SOLVER_INPUT_TEMPLATE.format(text=math_problem.latex).strip(),
                max_turns=15,
            )
            validator_result = await Runner.run(
                katex_validator_agent,
                input=KATEX_VALIDATOR_INPUT_TEMPLATE.format(
                    text=solver_result.final_output
                ).strip(),
                max_turns=50,
            )

        finally:
            await self.jupyter_client.end_session(user_id='0')

        solution = MathProblemSolution()  # TODO update type, use validator_result.final_output
        # TODO save to repo
        return
