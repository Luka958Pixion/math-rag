import asyncio

from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from math_rag.mcp.base import BaseTool


class ToolResult(BaseModel):
    message: str


class MathProblemSolverTool(BaseTool):
    async def solve(
        self,
        image_url: str,
    ) -> ToolResult:
        if len(image_url) == 0:
            raise HTTPException(400, 'Uploaded image is empty.')

        await asyncio.sleep(2)

        return ToolResult(
            message='Problem validated. Next, please upload your literature PDF for indexing.'
        )

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.solve,
            name=self.__class__.__name__,
            description='Validates the math problem input before any indexing.',
            annotations=ToolAnnotations(title='Validate problem'),
        )
