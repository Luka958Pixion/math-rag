import asyncio

from logging import ERROR, INFO, WARNING, basicConfig, getLogger

import uvicorn

from decouple import config

import math_rag.mcp.resources as resources
import math_rag.mcp.tools as tools
import math_rag.web.routers as routers

from math_rag.infrastructure.containers import InfrastructureContainer
from math_rag.mcp import create_mcp
from math_rag.web import create_api


HOST = config('HOST')
API_PORT = config('API_PORT', cast=int)
MCP_PORT = config('MCP_PORT', cast=int)


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
getLogger('pylatexenc.latexwalker').setLevel(ERROR)
getLogger('httpx').setLevel(WARNING)
getLogger('openai').setLevel(WARNING)

logger = getLogger(__name__)


async def main():
    # inject dependecies
    infrastructure_container = InfrastructureContainer()
    infrastructure_container.init_resources()
    infrastructure_container.wire(modules=[__name__])

    application_container = infrastructure_container.application_container()
    application_container.init_resources()
    application_container.wire(modules=[__name__])
    application_container.wire(packages=[routers, tools, resources])

    # seed
    for object_seeder in infrastructure_container.object_seeders():
        object_seeder.seed()

    for document_seeder in infrastructure_container.document_seeders():
        await document_seeder.seed()

    # index
    for document_indexer in infrastructure_container.document_indexers():
        await document_indexer.index()

    # serve
    api = create_api(application_container)
    api_uvicorn_config = uvicorn.Config(
        api,
        host=HOST,
        port=API_PORT,
        loop='asyncio',
        log_level='info',
    )
    api_uvicorn_server = uvicorn.Server(api_uvicorn_config)

    mcp = create_mcp()
    mcp_uvicorn_config = uvicorn.Config(
        mcp,
        host=HOST,
        port=MCP_PORT,
        loop='asyncio',
        log_level='info',
    )
    mcp_uvicorn_server = uvicorn.Server(mcp_uvicorn_config)

    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(api_uvicorn_server.serve(), name='API')
        task_group.create_task(mcp_uvicorn_server.serve(), name='MCP')

    application_container.shutdown_resources()
    infrastructure_container.shutdown_resources()


if __name__ == '__main__':
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        pass
