from logging import getLogger
from pathlib import Path

from agents import Runner
from httpx import AsyncClient

from math_rag.application.agents import (
    KATEX_VALIDATOR_INPUT_TEMPLATE,
    MATH_PROBLEM_SOLVER_INPUT_TEMPLATE,
    KatexValidatorAgent,
    MathProblemSolverAgent,
)
from math_rag.application.base.clients import BaseJupyterClient, BaseLatexConverterClient
from math_rag.application.base.services import BaseMathProblemSolverService
from math_rag.application.utils import MagicBytesWriterUtil
from math_rag.core.models import MathProblem, MathProblemSolution


DOWNLOADS_DIR_PATH = Path(__file__).parents[3] / '.tmp' / 'downloads'

logger = getLogger(__name__)


class MathProblemSolverService(BaseMathProblemSolverService):
    def __init__(
        self, jupyter_client: BaseJupyterClient, latex_converter_client: BaseLatexConverterClient
    ):
        self.jupyter_client = jupyter_client
        self.latex_converter_client = latex_converter_client

    async def solve(self, math_problem: MathProblem) -> MathProblemSolution:
        if math_problem.url and '/api/v1/download-shared-object' in math_problem.url:
            async with AsyncClient() as client:
                url = math_problem.url.replace('localhost', 'minio')  # NOTE: not clean
                response = await client.get(url)
                response.raise_for_status()

            math_problem.file_path = await MagicBytesWriterUtil.write(
                response.content,
                DOWNLOADS_DIR_PATH,
                allowed_content_types=self.latex_converter_client.list_content_types(),
            )
            math_problem.url = None

        latex = self.latex_converter_client.convert_image(
            file_path=math_problem.file_path, url=math_problem.url
        )

        try:
            await self.jupyter_client.start_session(user_id='0')

            math_problem_solver_agent = MathProblemSolverAgent(
                math_problem.math_expression_index_id
            )
            katex_validator_agent = KatexValidatorAgent()

            solver_result = await Runner.run(
                math_problem_solver_agent,
                input=MATH_PROBLEM_SOLVER_INPUT_TEMPLATE.format(text=latex).strip(),
                max_turns=15,
            )
            validator_result = await Runner.run(
                katex_validator_agent,
                input=KATEX_VALIDATOR_INPUT_TEMPLATE.format(
                    text=solver_result.final_output
                ).strip(),
                max_turns=50,
            )
            return MathProblemSolution(
                math_problem_id=math_problem.id, text=validator_result.final_output
            )

        except Exception as e:
            logger.error(f'Math problem solving failed with: {e}')

            return MathProblemSolution(
                math_problem_id=math_problem.id, text='Math problem solving failed'
            )

        finally:
            await self.jupyter_client.end_session(user_id='0')
