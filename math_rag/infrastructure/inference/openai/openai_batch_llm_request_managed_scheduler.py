from collections.abc import AsyncGenerator

from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseBatchLLMRequestScheduler,
)
from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchRequestSchedule,
    LLMBatchResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIBatchLLMRequestManagedScheduler(BaseBatchLLMRequestManagedScheduler):
    def __init__(
        self,
        scheduler: BaseBatchLLMRequestScheduler,
        llm_settings_loader_service: BaseLLMSettingsLoaderService,
    ):
        self.scheduler = scheduler
        self.llm_settings_loader_service = llm_settings_loader_service

    def schedule(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> LLMBatchRequestSchedule[LLMResponseType]:
        if not batch_request.requests:
            raise ValueError(f'Batch request {batch_request.id} is empty')

        model = batch_request.requests[0].params.model
        batch_settings = self.llm_settings_loader_service.load_batch_settings('openai', model)

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
        schedule: LLMBatchRequestSchedule[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> AsyncGenerator[LLMBatchResult[LLMResponseType], None]:
        async for batch_result in self.scheduler.execute(schedule, response_type):
            yield batch_result
