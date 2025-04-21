from math_rag.application.base.inference import (
    BaseConcurrentLLM,
    BaseConcurrentManagedLLM,
)
from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.inference import (
    LLMConcurrentRequest,
    LLMConcurrentResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIConcurrentManagedLLM(BaseConcurrentManagedLLM):
    def __init__(
        self,
        llm: BaseConcurrentLLM,
        llm_settings_loader_service: BaseLLMSettingsLoaderService,
    ):
        self._llm = llm
        self._llm_settings_loader_service = llm_settings_loader_service

    async def concurrent_generate(
        self, concurrent_request: LLMConcurrentRequest[LLMResponseType]
    ) -> LLMConcurrentResult[LLMResponseType]:
        concurrent_settings = (
            self._llm_settings_loader_service.load_concurrent_settings(
                'openai', concurrent_request.requests[0].params.model
            )
        )

        return await self._llm.concurrent_generate(
            concurrent_request,
            max_requests_per_minute=concurrent_settings.max_requests_per_minute,
            max_tokens_per_minute=concurrent_settings.max_tokens_per_minute,
            max_num_retries=concurrent_settings.max_num_retries,
        )
