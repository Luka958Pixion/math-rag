from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from math_rag.mcp.base import BaseTool
from math_rag.mcp.constants import OPENAPI_URL, TITLE
from math_rag.mcp.tools import (
    SolveProblemTool,
    ValidateDocumentTool,
    ValidateProblemTool,
)


# TODO implement this: https://chatgpt.com/share/6838d5e0-68a0-8007-a39c-da1abcc53e6f
# TODO do we need DI? is it better to just consume endpoints?


def create_mcp() -> FastAPI:
    mcp = FastMCP(
        name=TITLE,
        stateless_http=True,
        enable_discovery_routes=True,
    )
    tools: list[BaseTool] = [
        SolveProblemTool(),
        ValidateDocumentTool(),
        ValidateProblemTool(),
    ]

    for tool in tools:
        tool.add(mcp)

    api = FastAPI(
        title=TITLE,
        openapi_url=OPENAPI_URL,
        lifespan=lambda: mcp.session_manager.run(),
    )

    api.mount('/', mcp.streamable_http_app())

    return api
