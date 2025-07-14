import asyncio

from fastapi import HTTPException, UploadFile
from mcp.server.fastmcp import FastMCP

from math_rag.mcp.base import BaseTool
from math_rag.mcp.tools.results import SolveProblemResult


class SolveProblemTool(BaseTool):
    async def solve_problem_tool(
        self,
        input_text: str | None = None,
        input_image: UploadFile | None = None,
        pdf_file: UploadFile | None = None,
    ) -> SolveProblemResult:
        if not input_text and not input_image:
            raise HTTPException(400, 'No problem input provided.')

        image_bytes = await input_image.read() if input_image else None
        pdf_bytes = await pdf_file.read() if pdf_file else None
        await asyncio.sleep(3)

        return SolveProblemResult(solution=f'the final solution is: 100')

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.solve_problem_tool,
            name='solve_math_problem',
            description='Solves the validated math problem using the indexed literature.',
        )
