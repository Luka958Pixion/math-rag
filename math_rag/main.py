import asyncio

from contextlib import asynccontextmanager, suppress
from logging import ERROR, INFO, WARNING, basicConfig, getLogger

import uvicorn

from decouple import config
from fastapi import FastAPI

from math_rag.application.containers import ApplicationContainer
from math_rag.infrastructure.containers import InfrastructureContainer
from math_rag.web.constants import OPENAPI_URL, TITLE
from math_rag.web.routers.index import index_create_router, index_worker


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
getLogger('pylatexenc.latexwalker').setLevel(ERROR)
getLogger('httpx').setLevel(WARNING)
getLogger('openai').setLevel(WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background worker on startup
    worker = asyncio.create_task(index_worker(), name='index_worker')
    yield

    # On shutdown, cancel and await the worker
    worker.cancel()

    with suppress(asyncio.CancelledError):
        await worker


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

    app = FastAPI(openapi_url=OPENAPI_URL, title=TITLE, lifespan=lifespan)
    app.include_router(index_create_router)

    uvicorn.run(app, host=config('HOST'), port=config('PORT'))


if __name__ == '__main__':
    asyncio.run(main())
