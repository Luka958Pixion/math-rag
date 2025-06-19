import asyncio

from logging import getLogger
from typing import Awaitable

from math_rag.application.base.repositories.documents.partials import BaseTaskTrackerRepository
from math_rag.application.base.services.backgrounds import BaseTaskTrackerBackgroundService
from math_rag.application.contexts import TaskContext
from math_rag.core.enums import TaskStatus


logger = getLogger(__name__)


class TaskTrackerBackgroundService(BaseTaskTrackerBackgroundService):
    def __init__(
        self,
        task_tracker_repository: BaseTaskTrackerRepository,
        task_context: TaskContext,
    ):
        self.task_tracker_repository = task_tracker_repository
        self.task_context = task_context

    async def track(self, awaitable: Awaitable[None], timeout: float | None):
        while True:
            # wait until notified
            async with self.task_context.condition:
                await self.task_context.condition.wait()

            # only one build at a time
            async with self.task_context.lock:
                current_index = await self.task_tracker_repository.find_first_pending()

                if not current_index:
                    continue

                current_index = await self.task_tracker_repository.update_task_status(
                    current_index.id, TaskStatus.RUNNING
                )

                try:
                    # timeout each build to avoid hangs
                    await asyncio.wait_for(awaitable, timeout)

                    current_index = await self.task_tracker_repository.update_task_status(
                        current_index.id, TaskStatus.FINISHED
                    )
                    logger.info(f'Index {current_index.id} build finished')

                except asyncio.TimeoutError:
                    current_index = await self.task_tracker_repository.update_task_status(
                        current_index.id, TaskStatus.FAILED
                    )
                    logger.warning(f'Index {current_index.id} build failed due to a time out')

                except Exception as e:
                    current_index = await self.task_tracker_repository.update_task_status(
                        current_index.id, TaskStatus.FAILED
                    )
                    logger.exception(f'Index {current_index.id} build failed due to an error: {e}')
