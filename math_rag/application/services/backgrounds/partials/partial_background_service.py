from asyncio import sleep
from logging import getLogger

from math_rag.application.base.repositories.documents import BaseTaskRepository
from math_rag.application.base.services.backgrounds import BaseBackgroundService
from math_rag.core.enums import TaskStatus


logger = getLogger(__name__)


class PartialBackgroundService(BaseBackgroundService):
    def __init__(self, task_repository: BaseTaskRepository):
        self.task_repository = task_repository

    async def start(self):
        while True:
            task_model_type = self.task_model_name()
            task = await self.task_repository.find_first_pending(task_model_type)

            if not task:
                await sleep(30)
                continue

            task = await self.task_repository.update_task_status(task.id, TaskStatus.RUNNING)

            try:
                await self.task(task.model_id)
                task = await self.task_repository.update_task_status(task.id, TaskStatus.FINISHED)
                logger.info(f'Task {task.id} finished')

            except Exception as e:
                task = await self.task_repository.update_task_status(task.id, TaskStatus.FAILED)
                logger.exception(f'Task {task.id} failed due to an error: {e}')
