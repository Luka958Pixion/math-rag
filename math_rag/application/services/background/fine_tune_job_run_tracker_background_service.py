import asyncio

from logging import getLogger

from math_rag.application.base.fine_tune import BaseFineTuneJobRunnerService
from math_rag.application.base.repositories.documents import BaseFineTuneJobRepository
from math_rag.application.base.services.background import BaseFineTuneJobRunTrackerBackgroundService
from math_rag.application.contexts import FineTuneJobRunContext
from math_rag.core.enums import FineTuneJobRunStatus


TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)


class FineTuneJobRunTrackerBackgroundService(BaseFineTuneJobRunTrackerBackgroundService):
    def __init__(
        self,
        fine_tune_job_repository: BaseFineTuneJobRepository,
        fine_tune_job_runner_service: BaseFineTuneJobRunnerService,
        fine_tune_job_run_context: FineTuneJobRunContext,
    ):
        self.fine_tune_job_repository = fine_tune_job_repository
        self.fine_tune_job_runner_service = fine_tune_job_runner_service
        self.fine_tune_job_run_context = fine_tune_job_run_context

    async def track(self):
        while True:
            # wait until notified
            async with self.fine_tune_job_run_context.condition:
                await self.fine_tune_job_run_context.condition.wait()

            # only one build at a time
            async with self.fine_tune_job_run_context.lock:
                current_fine_tune_job = await self.fine_tune_job_repository.find_first_pending()

                if not current_fine_tune_job:
                    continue

                current_fine_tune_job = await self.fine_tune_job_repository.update_build_status(
                    current_fine_tune_job.id, FineTuneJobRunStatus.RUNNING
                )

                try:
                    # timeout each build to avoid hangs
                    await asyncio.wait_for(
                        self.fine_tune_job_runner_service.build(current_fine_tune_job),
                        timeout=TIMEOUT,
                    )
                    current_fine_tune_job = await self.fine_tune_job_repository.update_build_status(
                        current_fine_tune_job.id, FineTuneJobRunStatus.FINISHED
                    )
                    logger.info(f'Fine tune job {current_fine_tune_job.id} run finished')

                except asyncio.TimeoutError:
                    current_fine_tune_job = await self.fine_tune_job_repository.update_build_status(
                        current_fine_tune_job.id, FineTuneJobRunStatus.FAILED
                    )
                    logger.warning(
                        f'Fine tune job {current_fine_tune_job.id} run failed due to a time out'
                    )

                except Exception as e:
                    current_fine_tune_job = await self.fine_tune_job_repository.update_build_status(
                        current_fine_tune_job.id, FineTuneJobRunStatus.FAILED
                    )
                    logger.exception(
                        f'Fine tune job {current_fine_tune_job.id} run failed due to an error: {e}'
                    )
