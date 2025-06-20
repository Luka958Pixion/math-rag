import asyncio

from logging import getLogger

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.base.services import BaseIndexBuilderService
from math_rag.application.base.services.background import (
    BaseIndexBuildTrackerBackgroundService,
)
from math_rag.application.contexts import IndexBuildContext
from math_rag.core.enums import IndexBuildStatus


TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)


class IndexBuildTrackerBackgroundService(BaseIndexBuildTrackerBackgroundService):
    def __init__(
        self,
        index_repository: BaseIndexRepository,
        index_builder_service: BaseIndexBuilderService,
        index_build_context: IndexBuildContext,
    ):
        self.index_repository = index_repository
        self.index_builder_service = index_builder_service
        self.index_build_context = index_build_context

    async def track(self):
        while True:
            # wait until notified
            async with self.index_build_context.condition:
                await self.index_build_context.condition.wait()

            # only one build at a time
            async with self.index_build_context.lock:
                current_index = await self.index_repository.find_first_pending()

                if not current_index:
                    continue

                current_index = await self.index_repository.update_build_status(
                    current_index.id, IndexBuildStatus.RUNNING
                )

                try:
                    # timeout each build to avoid hangs
                    await asyncio.wait_for(
                        self.index_builder_service.build(current_index),
                        timeout=TIMEOUT,
                    )
                    current_index = await self.index_repository.update_build_status(
                        current_index.id, IndexBuildStatus.FINISHED
                    )
                    logger.info(f'Index {current_index.id} build finished')

                except asyncio.TimeoutError:
                    current_index = await self.index_repository.update_build_status(
                        current_index.id, IndexBuildStatus.FAILED
                    )
                    logger.warning(f'Index {current_index.id} build failed due to a time out')

                except Exception as e:
                    current_index = await self.index_repository.update_build_status(
                        current_index.id, IndexBuildStatus.FAILED
                    )
                    logger.exception(f'Index {current_index.id} build failed due to an error: {e}')
