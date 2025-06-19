import asyncio
import os
import signal

from contextlib import asynccontextmanager, suppress
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from math_rag.application.containers import ApplicationContainer
from math_rag.web.constants import OPENAPI_URL, TITLE
from math_rag.web.routers import routers


logger = getLogger(__name__)


def root():
    return {'title': TITLE}


def on_exception(task: asyncio.Task):
    if task.cancelled():
        return

    exception = task.exception()

    if exception:
        logger.error(
            f'Task {task.get_name()} crashed, shutting down!',
            exc_info=exception,
        )

        # send SIGTERM to self so uvicorn will exit gracefully
        os.kill(os.getpid(), signal.SIGTERM)


@asynccontextmanager
async def lifespan(api: FastAPI):
    application_container: ApplicationContainer = api.state.application_container
    tasks = [
        asyncio.create_task(service.start(), name=service.__class__.__name__)
        for service in application_container.background_services()
    ]

    for task in tasks:
        task.add_done_callback(on_exception)

    yield

    for task in tasks:
        task.cancel()

    with suppress(asyncio.CancelledError):
        await asyncio.gather(*tasks)


async def global_exception_handler(request: Request, exception: Exception):
    logger.error(f'Unhandled exception: {exception}')

    return JSONResponse(
        status_code=500,
        content={'success': False, 'error': 'Internal Server Error'},
    )


def create_api(application_container: ApplicationContainer) -> FastAPI:
    api = FastAPI(
        title=TITLE,
        openapi_url=OPENAPI_URL,
        lifespan=lifespan,
    )
    api.state.application_container = application_container

    api.add_api_route('/', root, methods=['GET'])

    for router in routers:
        api.include_router(router)

    api.add_exception_handler(Exception, global_exception_handler)

    return api
