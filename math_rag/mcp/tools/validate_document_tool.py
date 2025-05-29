from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException, UploadFile
from mcp.server.fastmcp import FastMCP

from math_rag.application.containers import ApplicationContainer


def validate_document_tool(
    pdf_file: UploadFile,
) -> dict:
    if pdf_file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=400, detail='Only PDF files are accepted as literature references.'
        )

    head = pdf_file.file.read(4)
    if not head or head != b'%PDF':
        raise HTTPException(status_code=400, detail='Uploaded file is not a valid PDF document.')

    return {
        'message': 'Literature PDF validated. You may now solve the problem using solve_math_problem.'
    }


def add_validate_document_tool(mcp: FastMCP):
    mcp.add_tool(
        validate_document_tool,
        name='validate_document',
        description='Validate uploaded literature file (PDF only).',
        annotations={
            'pdf_file': {'type': 'string', 'format': 'binary'},
        },
    )
