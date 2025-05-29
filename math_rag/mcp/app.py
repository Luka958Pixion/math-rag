from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from math_rag.application.containers import ApplicationContainer
from math_rag.mcp.constants import NAME
from math_rag.mcp.tools import echo_tool


def create_mcp_app(application_container: ApplicationContainer) -> FastAPI:
    mcp = FastMCP(
        name=NAME,
        # lifespan=None,
        stateless_http=True,
        enable_discovery_routes=True,
    )

    mcp.add_tool(echo_tool, name=None, description=None, annotations=None)
    # mcp.add_prompt()
    # mcp.add_resource()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with mcp.session_manager.run():
            yield

    mcp_app = FastAPI(lifespan=lifespan)
    mcp_app.mount('/', mcp.streamable_http_app())

    return mcp_app
