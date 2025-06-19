from asyncio import sleep
from logging import getLogger

from math_rag.application.base.repositories.documents import BaseTaskRepository
from math_rag.application.base.services.backgrounds import BaseTaskTrackerBackgroundService
from math_rag.core.enums import TaskStatus


logger = getLogger(__name__)


class PartialTaskTrackerBackgroundService(BaseTaskTrackerBackgroundService):
    def __init__(self, task_repository: BaseTaskRepository):
        self.task_repository = task_repository

    async def track(self):
        while True:
            task = await self.task_repository.find_first_pending()

            if not task:
                sleep(30)
                continue

            task = await self.task_repository.update_task_status(task.id, TaskStatus.RUNNING)

            try:
                await self.task()
                task = await self.task_repository.update_task_status(task.id, TaskStatus.FINISHED)
                logger.info(f'Task {task.id} finished')

            except Exception as e:
                task = await self.task_repository.update_task_status(task.id, TaskStatus.FAILED)
                logger.exception(f'Task {task.id} failed due to an error: {e}')
