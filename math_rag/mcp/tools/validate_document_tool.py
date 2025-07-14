import asyncio

from fastapi import HTTPException, UploadFile
from mcp.server.fastmcp import FastMCP

from math_rag.mcp.base import BaseTool
from math_rag.mcp.tools.results import ValidateDocumentResult


class ValidateDocumentTool(BaseTool):
    async def validate_document_tool(
        self,
        pdf_file: UploadFile,
    ) -> ValidateDocumentResult:
        if pdf_file.content_type != 'application/pdf':
            raise HTTPException(400, 'Only PDF files are accepted.')

        header = await pdf_file.read(4)

        if header != b'%PDF':
            raise HTTPException(400, 'Uploaded file is not a valid PDF.')

        # TODO: replace with real indexing
        asyncio.sleep(3)

        return ValidateDocumentResult(
            message=f'Literature indexing has completed. You may now submit your problem.'
        )

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.validate_document_tool,
            name='validate_document',
            description='Validates the PDF and initiates indexing.',
        )
