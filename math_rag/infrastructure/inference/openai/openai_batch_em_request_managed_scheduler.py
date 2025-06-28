from collections.abc import AsyncGenerator

from math_rag.application.base.inference import BaseBatchEMRequestManagedScheduler
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchRequestSchedule,
    EMBatchResult,
)

from .openai_batch_em_request_scheduler import OpenAIBatchEMRequestScheduler


class OpenAIBatchEMRequestManagedScheduler(BaseBatchEMRequestManagedScheduler):
    def __init__(
        self,
        scheduler: OpenAIBatchEMRequestScheduler,
        em_settings_loader_service: BaseEMSettingsLoaderService,
    ):
        self.scheduler = scheduler
        self.em_settings_loader_service = em_settings_loader_service

    def schedule(
        self,
        batch_request: EMBatchRequest,
    ) -> EMBatchRequestSchedule:
        if not batch_request.requests:
            raise ValueError(f'Batch request {batch_request.id} is empty')

        model = batch_request.requests[0].params.model
        batch_settings = self.em_settings_loader_service.load_batch_settings('openai', model)

        if batch_settings.max_tokens_per_day is None:
            raise ValueError('max_num_retries can not be None')

        elif batch_settings.max_input_file_size is None:
            raise ValueError('max_input_file_size can not be None')

        return self.scheduler.schedule(
            batch_request,
            max_tokens_per_day=batch_settings.max_tokens_per_day,
            max_input_file_size=batch_settings.max_input_file_size,
        )

    async def execute(
        self,
        schedule: EMBatchRequestSchedule,
    ) -> AsyncGenerator[EMBatchResult, None]:
        async for batch_result in self.scheduler.execute(schedule):
            yield batch_result
