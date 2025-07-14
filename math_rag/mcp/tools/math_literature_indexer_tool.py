import asyncio

from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from math_rag.mcp.base import BaseTool


class ToolResult(BaseModel):
    message: str


class MathLiteratureIndexerTool(BaseTool):
    async def index(self, pdf_url: str) -> ToolResult:
        if not pdf_url:
            raise HTTPException(400, 'Uploaded PDF is empty.')

        await asyncio.sleep(2)

        return ToolResult(
            message='Literature indexing completed. You may now ask for the solution.'
        )

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.index,
            name='validate_literature',
            description='Validates the PDF and initiates indexing after problem validation.',
            annotations=ToolAnnotations(title='Validate literature'),
        )
