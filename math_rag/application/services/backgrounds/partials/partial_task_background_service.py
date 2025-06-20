from asyncio import sleep
from logging import getLogger

from math_rag.application.base.repositories.documents import BaseTaskRepository
from math_rag.application.base.services.backgrounds import BaseTaskBackgroundService
from math_rag.core.enums import TaskStatus


logger = getLogger(__name__)
POLL_INTERVAL = 60


class PartialTaskBackgroundService(BaseTaskBackgroundService):
    def __init__(self, task_repository: BaseTaskRepository):
        self.task_repository = task_repository

    async def start(self):
        while True:
            task_model_name = self.task_model_name()
            task = await self.task_repository.find_first_pending(task_model_name)

            if not task:
                await sleep(POLL_INTERVAL)
                continue

            task = await self.task_repository.update_task_status(task.id, TaskStatus.RUNNING)

            try:
                await self.task(task.model_id)
                task = await self.task_repository.update_task_status(task.id, TaskStatus.FINISHED)
                logger.info(f'Task {task.id} finished')

            except Exception as e:
                task = await self.task_repository.update_task_status(task.id, TaskStatus.FAILED)
                logger.exception(f'Task {task.id} failed due to an error: {e}')
