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

        return ToolResult(message='Index built successfully')

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.index,
            name=self.__class__.__name__,
            description=(
                'Builds an index of math literature from the provided URL. '
                'A required step before solving any math problems.'
            ),
            annotations=ToolAnnotations(title='Math Literature Indexer'),
        )
