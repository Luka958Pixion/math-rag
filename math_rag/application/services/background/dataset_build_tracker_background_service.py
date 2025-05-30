import asyncio

from logging import getLogger

from math_rag.application.base.repositories.documents import BaseDatasetRepository
from math_rag.application.base.services import BaseMathExpressionDatasetBuilderService
from math_rag.application.base.services.background import (
    BaseDatasetBuildTrackerBackgroundService,
)
from math_rag.application.contexts import DatasetBuildContext
from math_rag.core.enums import DatasetBuildStatus


BUILD_DATASET_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

logger = getLogger(__name__)


class DatasetBuildTrackerBackgroundService(BaseDatasetBuildTrackerBackgroundService):
    def __init__(
        self,
        dataset_repository: BaseDatasetRepository,
        dataset_builder_service: BaseMathExpressionDatasetBuilderService,
        dataset_build_context: DatasetBuildContext,
    ):
        self.dataset_repository = dataset_repository
        self.dataset_builder_service = dataset_builder_service
        self.dataset_build_context = dataset_build_context

    async def track(self):
        while True:
            # wait until notified
            async with self.dataset_build_context.condition:
                await self.dataset_build_context.condition.wait()

            # only one build at a time
            async with self.dataset_build_context.lock:
                current_dataset = await self.dataset_repository.find_first_pending()

                if not current_dataset:
                    continue

                current_dataset = await self.dataset_repository.update_build_status(
                    current_dataset.id, DatasetBuildStatus.RUNNING
                )

                try:
                    # timeout each build to avoid hangs
                    await asyncio.wait_for(
                        self.dataset_builder_service.build(current_dataset),
                        timeout=BUILD_DATASET_TIMEOUT,
                    )
                    current_dataset = await self.dataset_repository.update_build_status(
                        current_dataset.id, DatasetBuildStatus.FINISHED
                    )
                    logger.info(f'Dataset {current_dataset.id} build finished')

                except asyncio.TimeoutError:
                    current_dataset = await self.dataset_repository.update_build_status(
                        current_dataset.id, DatasetBuildStatus.FAILED
                    )
                    logger.warning(f'Dataset {current_dataset.id} build failed due to a time out')

                except Exception as e:
                    current_dataset = await self.dataset_repository.update_build_status(
                        current_dataset.id, DatasetBuildStatus.FAILED
                    )
                    logger.exception(
                        f'Dataset {current_dataset.id} build failed due to an error: {e}'
                    )
