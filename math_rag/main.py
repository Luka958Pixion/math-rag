import asyncio

from logging import ERROR, INFO, WARNING, basicConfig, getLogger

import uvicorn

from decouple import config
from fastapi import FastAPI

import math_rag.mcp.resources as resources
import math_rag.mcp.tools as tools
import math_rag.web.routers as routers

from math_rag.infrastructure.containers import InfrastructureContainer
from math_rag.mcp import create_mcp_app
from math_rag.web import create_api_app


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
    math_article_seeder = infrastructure_container.math_article_seeder()
    math_expression_seeder = infrastructure_container.math_expression_seeder()
    math_expression_label_seeder = infrastructure_container.math_expression_label_seeder()

    math_article_seeder.seed()
    await math_expression_seeder.seed()
    await math_expression_label_seeder.seed()

    core_app = create_api_app(application_container)
    mcp_app = create_mcp_app(application_container)

    # unified = FastAPI()
    # unified.mount("/mcp", mcp_app)
    # unified.mount("/api", core_app)

    uvicorn_config = uvicorn.Config(
        core_app,
        host=config('HOST'),
        port=config('PORT', cast=int),
        loop='asyncio',
        log_level='info',
    )
    uvicorn_server = uvicorn.Server(uvicorn_config)

    uvicorn_config2 = uvicorn.Config(
        mcp_app,
        host=config('HOST'),
        port=7200,
        loop='asyncio',
        log_level='info',
    )
    uvicorn_server2 = uvicorn.Server(uvicorn_config2)

    await asyncio.gather(
        asyncio.create_task(uvicorn_server.serve()), asyncio.create_task(uvicorn_server2.serve())
    )


if __name__ == '__main__':
    asyncio.run(main())
