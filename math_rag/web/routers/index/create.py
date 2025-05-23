import asyncio

from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer


logger = getLogger(__name__)
router = APIRouter()

# Synchronization primitives
auto_condition = asyncio.Condition()
build_lock = asyncio.Lock()

# In-memory store
index_repo: dict[int, str] = {}
next_id = 0


@router.post('/index/create')
@inject
async def create_index(
    index_repository: BaseIndexRepository = Depends(
        Provide[ApplicationContainer.index_repository]
    ),
):
    global next_id
    idx = next_id
    next_id += 1
    index_repo[idx] = 'pending'

    # Notify the worker immediately
    async with auto_condition:
        auto_condition.notify()

    return {'id': idx, 'status': index_repo[idx]}


async def build_index(idx: int):
    logger.info(f'Starting build for index {idx}')
    # Offload blocking or CPU-heavy logic to a thread
    await asyncio.to_thread(lambda i: None, idx)
    await asyncio.sleep(5)  # simulate work
    logger.info(f'Finished build for index {idx}')


async def index_worker():
    while True:
        # Wait until create_index notifies us
        async with auto_condition:
            await auto_condition.wait()

        # Only one build at a time
        async with build_lock:
            pending = [i for i, s in index_repo.items() if s == 'pending']

            if not pending:
                continue

            idx = pending[0]
            index_repo[idx] = 'building'

            try:
                # Timeout each build to avoid hangs
                await asyncio.wait_for(build_index(idx), timeout=60)
                index_repo[idx] = 'done'
                logger.info(f'Index {idx} done')

            except asyncio.TimeoutError:
                index_repo[idx] = 'failed'
                logger.warning(f'Index {idx} timed out')

            except Exception as e:
                index_repo[idx] = 'failed'
                logger.exception(f'Index {idx} error: {e}')
