import asyncio

from contextlib import asynccontextmanager, suppress
from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from math_rag.application.base.services import BaseIndexBuildTrackerService
from math_rag.application.containers import ApplicationContainer
from math_rag.web.constants import OPENAPI_URL, TITLE
from math_rag.web.routers.index import index_create_router


logger = getLogger(__name__)


@asynccontextmanager
@inject
async def lifespan(
    app: FastAPI,
    index_build_tracker_service: BaseIndexBuildTrackerService = Depends(
        Provide[ApplicationContainer.index_build_tracker_service]
    ),
):
    # start IndexBuildTrackerService on startup
    worker = asyncio.create_task(
        index_build_tracker_service.track(),
        name=index_build_tracker_service.__class__.__name__,
    )
    yield

    # cancel and await IndexBuildTrackerService on shutdown
    worker.cancel()

    with suppress(asyncio.CancelledError):
        await worker


app = FastAPI(openapi_url=OPENAPI_URL, title=TITLE, lifespan=lifespan)
app.include_router(index_create_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exception: Exception):
    logger.error(f'Unhandled exception: {exception}')

    return JSONResponse(
        status_code=500, content={'success': False, 'error': 'Internal Server Error'}
    )
