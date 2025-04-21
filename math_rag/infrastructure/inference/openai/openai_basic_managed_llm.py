from math_rag.application.base.inference import BaseBasicManagedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.inference import (
    LLMRequest,
    LLMResult,
)
from math_rag.application.types.inference import LLMResponseType

from .openai_basic_llm import OpenAIBasicLLM


class OpenAIBasicManagedLLM(BaseBasicManagedLLM):
    def __init__(
        self,
        llm: OpenAIBasicLLM,
        llm_settings_loader_service: BaseLLMSettingsLoaderService,
        llm_failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self._llm = llm
        self._llm_settings_loader_service = llm_settings_loader_service
        self._llm_failed_request_repository = llm_failed_request_repository

    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> LLMResult[LLMResponseType]:
        basic_settings = self._llm_settings_loader_service.load_basic_settings(
            'openai', request.params.model
        )

        if basic_settings.max_time is None:
            raise ValueError('max_time can not be None')

        elif basic_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        result = await self._llm.generate(
            request,
            max_time=basic_settings.max_time,
            max_num_retries=basic_settings.max_num_retries,
        )

        if result.failed_request:
            await self._llm_failed_request_repository.insert_one(result.failed_request)

        return result
