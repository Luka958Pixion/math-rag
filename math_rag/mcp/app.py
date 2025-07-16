from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from math_rag.mcp.base import BasePrompt, BaseResource, BaseTool
from math_rag.mcp.constants import OPENAPI_URL, TITLE
from math_rag.mcp.prompts import OfferSolvePrompt
from math_rag.mcp.resources import ConfigResource
from math_rag.mcp.tools import (
    IndexerTool,
    SolverTool,
)


def create_mcp() -> FastAPI:
    mcp = FastMCP(
        name=TITLE,
        stateless_http=True,
        enable_discovery_routes=True,
    )

    prompts: list[BasePrompt] = [
        # OfferSolvePrompt()
    ]

    for prompt in prompts:
        prompt.add(mcp)

    resources: list[BaseResource] = [
        # ConfigResource()
    ]

    for resource in resources:
        resource.add(mcp)

    tools: list[BaseTool] = [IndexerTool(), SolverTool()]

    for tool in tools:
        tool.add(mcp)

    api = FastAPI(
        title=TITLE,
        openapi_url=OPENAPI_URL,
        lifespan=lambda _: mcp.session_manager.run(),
    )

    api.mount('/', mcp.streamable_http_app())

    return api
