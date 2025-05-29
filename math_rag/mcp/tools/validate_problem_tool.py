from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException, UploadFile
from mcp.server.fastmcp import FastMCP

from math_rag.application.containers import ApplicationContainer


def validate_problem_tool(
    input_text: str | None = None,
    input_image: UploadFile | None = None,
) -> dict:
    if not input_text and not input_image:
        raise HTTPException(
            status_code=400,
            detail='No problem provided. Please submit the problem as text or upload an image.',
        )

    if input_image:
        if not input_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail='Uploaded file is not a valid image.')

        data = input_image.file.read()

        if not data:
            raise HTTPException(status_code=400, detail='Unable to read image file.')

    if input_text and not input_text.strip():
        raise HTTPException(status_code=400, detail='Problem text is empty.')

    return {'message': 'Problem validated. Please upload a PDF literature reference.'}


def add_validate_problem_tool(mcp: FastMCP):
    mcp.add_tool(
        validate_problem_tool,
        name='validate_problem',
        description='Ensure the user provided a valid math problem as text or image.',
        annotations={'input_text': str, 'input_image': UploadFile},
    )
