import asyncio

from logging import ERROR, INFO, WARNING, basicConfig, getLogger

import uvicorn

from decouple import config

import math_rag.web.routers as routers

from math_rag.infrastructure.containers import InfrastructureContainer
from math_rag.web import create_app


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
    application_container.wire(packages=[routers])

    # seed
    math_article_seeder = infrastructure_container.math_article_seeder()
    math_expression_seeder = infrastructure_container.math_expression_seeder()
    math_expression_label_seeder = (
        infrastructure_container.math_expression_label_seeder()
    )

    math_article_seeder.seed()
    await math_expression_seeder.seed()
    await math_expression_label_seeder.seed()

    app = create_app(application_container)
    uvicorn_config = uvicorn.Config(
        app,
        host=config('HOST'),
        port=int(config('PORT')),
        loop='asyncio',
        log_level='info',
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
