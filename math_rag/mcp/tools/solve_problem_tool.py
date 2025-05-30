from fastapi import HTTPException, UploadFile
from mcp.server.fastmcp import FastMCP

from math_rag.mcp.base import BaseTool


class SolveProblemTool(BaseTool):
    def solve_problem_tool(
        self,
        input_text: str | None = None,
        input_image: UploadFile | None = None,
        pdf_file: UploadFile | None = None,
    ) -> dict:
        if not input_text and not input_image:
            raise HTTPException(
                status_code=400,
                detail='No problem input provided. Please run validate_problem first.',
            )

        if pdf_file is None:
            return {'message': 'No literature provided. Solving based on problem statement only.'}

        full_pdf = pdf_file.file.read()
        if not full_pdf:
            raise HTTPException(status_code=400, detail='Failed to read PDF content.')

        # TODO: integrate LLM solver here
        solution = '[Solution placeholder]'

        return {'solution': solution}

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.solve_problem_tool,
            name='solve_math_problem',
            description='Solve the validated math problem using the optional literature reference.',
            annotations={
                'input_text': {'type': 'string'},
                'input_image': {'type': 'string', 'format': 'binary'},
                'pdf_file': {'type': 'string', 'format': 'binary'},
            },
        )
