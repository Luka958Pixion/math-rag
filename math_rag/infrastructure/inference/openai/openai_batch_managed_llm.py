from uuid import UUID

from math_rag.application.base.inference import BaseBatchLLM, BaseBatchManagedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIBatchManagedLLM(BaseBatchManagedLLM):
    def __init__(
        self,
        llm: BaseBatchLLM,
        llm_settings_loader_service: BaseLLMSettingsLoaderService,
        llm_failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self._llm = llm
        self._llm_settings_loader_service = llm_settings_loader_service
        self._llm_failed_request_repository = llm_failed_request_repository

    async def batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType]:
        batch_settings = self._llm_settings_loader_service.load_batch_settings(
            'openai', batch_request.requests[0].params.model
        )

        if batch_settings.poll_interval is None:
            raise ValueError('poll_interval can not be None')

        elif batch_settings.max_tokens_per_day is None:
            raise ValueError('max_num_retries can not be None')

        elif batch_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        batch_result = await self._llm.batch_generate(
            batch_request,
            response_type,
            poll_interval=batch_settings.poll_interval,
            max_tokens_per_day=batch_settings.max_tokens_per_day,
            max_num_retries=batch_settings.max_num_retries,
        )

        if batch_result.failed_requests:
            await self._llm_failed_request_repository.insert_many(
                batch_result.failed_requests
            )

        return batch_result

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        return await self._llm.batch_generate_init(batch_request)

    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType] | None:
        return await self._llm.batch_generate_result(
            batch_id, batch_request_id, response_type
        )
