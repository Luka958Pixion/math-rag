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
    index_service = application_container.index_build_tracker_background_service()
    dataset_service = application_container.dataset_build_tracker_background_service()

    index_task = asyncio.create_task(index_service.track(), name=index_service.__class__.__name__)
    dataset_task = asyncio.create_task(
        dataset_service.track(), name=dataset_service.__class__.__name__
    )

    index_task.add_done_callback(on_exception)
    dataset_task.add_done_callback(on_exception)

    yield

    for task in (index_task, dataset_task):
        task.cancel()

    with suppress(asyncio.CancelledError):
        await asyncio.gather(index_task, dataset_task)


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
        # dependency_overrides_provider=application_container,
    )
    api.state.application_container = application_container

    api.add_api_route('/', root, methods=['GET'])

    for router in routers:
        api.include_router(router)

    api.add_exception_handler(Exception, global_exception_handler)

    return api
