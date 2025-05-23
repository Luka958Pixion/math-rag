import asyncio

from contextlib import asynccontextmanager, suppress
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from math_rag.web.constants import OPENAPI_URL, TITLE
from math_rag.web.routers.index import index_create_router, index_worker


logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start the background worker on startup
    worker = asyncio.create_task(index_worker(), name='index_worker')
    yield

    # on shutdown, cancel and await the worker
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
