import asyncio

from logging import ERROR, INFO, WARNING, basicConfig, getLogger

import uvicorn

from decouple import config

from math_rag.application.containers import ApplicationContainer
from math_rag.infrastructure.containers import InfrastructureContainer
from math_rag.web import app


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
getLogger('pylatexenc.latexwalker').setLevel(ERROR)
getLogger('httpx').setLevel(WARNING)
getLogger('openai').setLevel(WARNING)

logger = getLogger(__name__)


async def main():
    infrastructure_container = InfrastructureContainer()
    infrastructure_container.application_container.override(application_container)
    infrastructure_container.init_resources()
    infrastructure_container.wire(modules=[__name__])

    application_container = ApplicationContainer(
        index_repository=infrastructure_container.index_repository
    )
    application_container.init_resources()
    application_container.wire(modules=[__name__])
    application_container.wire(packages=['web.routers'])

    # seed
    math_article_seeder = infrastructure_container.math_article_seeder()
    math_expression_seeder = infrastructure_container.math_expression_seeder()

    math_article_seeder.seed()
    await math_expression_seeder.seed()

    uvicorn.run(app, host=config('HOST'), port=config('PORT'))


if __name__ == '__main__':
    asyncio.run(main())
