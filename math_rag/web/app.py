import asyncio
import os
import signal

from contextlib import asynccontextmanager, suppress
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from math_rag.application.containers import ApplicationContainer
from math_rag.web.constants import OPENAPI_URL, TITLE
from math_rag.web.routers import health_router, scalar_router
from math_rag.web.routers.index import index_create_router


logger = getLogger(__name__)


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


def create_app(application_container: ApplicationContainer) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        index_build_tracker_service = (
            application_container.index_build_tracker_service()
        )
        task = asyncio.create_task(
            index_build_tracker_service.track(),
            name=index_build_tracker_service.__class__.__name__,
        )
        task.add_done_callback(on_exception)
        yield
        task.cancel()

        with suppress(asyncio.CancelledError):
            await task

    app = FastAPI(
        title=TITLE,
        openapi_url=OPENAPI_URL,
        lifespan=lifespan,
        dependency_overrides_provider=application_container,
    )

    # routers
    app.include_router(index_create_router)
    app.include_router(health_router)
    app.include_router(scalar_router)

    # exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exception: Exception):
        logger.error(f'Unhandled exception: {exception}')

        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': 'Internal Server Error'},
        )

    return app
