from fastapi import HTTPException, UploadFile

from math_rag.mcp.base import BaseTool
from math_rag.mcp.tools.results import ValidateProblemResult


class ValidateProblemTool(BaseTool):
    async def validate_problem_tool(
        self, input_text: str | None = None, input_image: UploadFile | None = None
    ) -> ValidateProblemResult:
        if not input_text and not input_image:
            raise HTTPException(400, 'No problem provided; submit text or an image.')

        if input_image:
            if not input_image.content_type.startswith('image/'):
                raise HTTPException(400, 'Uploaded file is not an image.')
            data = await input_image.read()
            if not data:
                raise HTTPException(400, 'Unable to read image.')

        if input_text and not input_text.strip():
            raise HTTPException(400, 'Problem text is empty.')

        return ValidateProblemResult(
            message='Problem validated; please upload the literature PDF next.'
        )

    def add(self, mcp):
        mcp.add_tool(
            self.validate_problem_tool,
            name='validate_problem',
            description='Validates the math problem input.',
        )
