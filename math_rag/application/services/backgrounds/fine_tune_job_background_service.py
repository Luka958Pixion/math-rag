from uuid import UUID

from math_rag.application.base.fine_tune import BaseFineTuneJobRunnerService
from math_rag.application.base.repositories.documents import (
    BaseFineTuneJobRepository,
    BaseTaskRepository,
)
from math_rag.core.models import FineTuneJob

from .partials import PartialBackgroundService


class FineTuneJobBackgroundService(PartialBackgroundService):
    def __init__(
        self,
        fine_tune_job_runner_service: BaseFineTuneJobRunnerService,
        fine_tune_job_repository: BaseFineTuneJobRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.fine_tune_job_runner_service = fine_tune_job_runner_service
        self.fine_tune_job_repository = fine_tune_job_repository

    async def task(self, task_model_id: UUID):
        job = await self.fine_tune_job_repository.find_one(filter=dict(id=task_model_id))

        if not job:
            raise ValueError()

        await self.fine_tune_job_runner_service.run(job, poll_interval=5 * 60)

    def task_model_name(self) -> str:
        return FineTuneJob.__name__
