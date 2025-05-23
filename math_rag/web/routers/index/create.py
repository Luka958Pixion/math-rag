import asyncio

from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.containers import ApplicationContainer
from math_rag.core.enums import IndexBuildStatus
from math_rag.core.models import Index
from math_rag.web.responses import IndexCreateResponse


BUILD_INDEX_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)
router = APIRouter()

# synchronization primitives
build_condition = asyncio.Condition()
build_lock = asyncio.Lock()


@router.post('/index/create', response_model=IndexCreateResponse)
@inject
async def create_index(
    index_repository: BaseIndexRepository = Depends(
        Provide[ApplicationContainer.index_repository]
    ),
):
    index = Index()
    await index_repository.insert_one(index)

    # notify the worker immediately
    async with build_condition:
        build_condition.notify()

    return IndexCreateResponse(**index.model_dump())


async def build_index(index: Index):
    logger.info(f'Starting build for index {index.id}')
    # offload blocking or CPU-heavy logic to a thread
    await asyncio.to_thread(lambda: None, index)  # TODO
    await asyncio.sleep(5)  # simulate work
    logger.info(f'Finished build for index {index.id}')


@inject
async def index_worker(
    index_repository: BaseIndexRepository = Provide[
        ApplicationContainer.index_repository
    ],
):
    while True:
        # wait until create_index runs notify()
        async with build_condition:
            await build_condition.wait()

        # only one build at a time
        async with build_lock:
            # indexes are already sorted by timestamp
            indexes = await index_repository.find_many()
            current_index: Index | None = None

            for index in indexes:
                if index.build_status == IndexBuildStatus.PENDING:
                    current_index = index
                    break

            if not current_index:
                continue

            current_index = await index_repository.update_build_status(
                current_index.id, IndexBuildStatus.RUNNING
            )

            try:
                # timeout each build to avoid hangs
                await asyncio.wait_for(
                    build_index(current_index), timeout=BUILD_INDEX_TIMEOUT
                )
                current_index = await index_repository.update_build_status(
                    current_index.id, IndexBuildStatus.FINISHED
                )
                logger.info(f'Index {current_index.id} build finished')

            except asyncio.TimeoutError:
                current_index = await index_repository.update_build_status(
                    current_index.id, IndexBuildStatus.FAILED
                )
                logger.warning(
                    f'Index {current_index.id} build failed due to a time out'
                )

            except Exception as e:
                current_index = await index_repository.update_build_status(
                    current_index.id, IndexBuildStatus.FAILED
                )
                logger.exception(f'Index {current_index.id} build due to an error: {e}')
