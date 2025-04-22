from math_rag.application.base.inference import BaseConcurrentManagedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.inference import (
    LLMConcurrentRequest,
    LLMConcurrentResult,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.validators.inference.openai import OpenAIValidator

from .openai_concurrent_llm import OpenAIConcurrentLLM


class OpenAIConcurrentManagedLLM(BaseConcurrentManagedLLM):
    def __init__(
        self,
        llm: OpenAIConcurrentLLM,
        llm_settings_loader_service: BaseLLMSettingsLoaderService,
        llm_failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self._llm = llm
        self._llm_settings_loader_service = llm_settings_loader_service
        self._llm_failed_request_repository = llm_failed_request_repository

    async def concurrent_generate(
        self, concurrent_request: LLMConcurrentRequest[LLMResponseType]
    ) -> LLMConcurrentResult[LLMResponseType]:
        model = concurrent_request.requests[0].params.model
        OpenAIValidator.validate_model_name(model)

        concurrent_settings = (
            self._llm_settings_loader_service.load_concurrent_settings('openai', model)
        )

        if concurrent_settings.max_requests_per_minute is None:
            raise ValueError('max_requests_per_minute can not be None')

        elif concurrent_settings.max_tokens_per_minute is None:
            raise ValueError('max_tokens_per_minute can not be None')

        elif concurrent_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        concurrent_result = await self._llm.concurrent_generate(
            concurrent_request,
            max_requests_per_minute=concurrent_settings.max_requests_per_minute,
            max_tokens_per_minute=concurrent_settings.max_tokens_per_minute,
            max_num_retries=concurrent_settings.max_num_retries,
        )

        if concurrent_result.failed_requests:
            await self._llm_failed_request_repository.insert_many(
                concurrent_result.failed_requests
            )

        return concurrent_result
