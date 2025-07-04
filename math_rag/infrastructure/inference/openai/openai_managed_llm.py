from math_rag.application.base.repositories.documents import BaseLLMFailedRequestRepository
from math_rag.application.base.services import BaseLLMSettingsLoaderService

from .openai_basic_managed_llm import OpenAIBasicManagedLLM
from .openai_batch_managed_llm import OpenAIBatchManagedLLM
from .openai_concurrent_managed_llm import OpenAIConcurrentManagedLLM
from .openai_llm import OpenAILLM


class OpenAIManagedLLM(OpenAIBasicManagedLLM, OpenAIBatchManagedLLM, OpenAIConcurrentManagedLLM):
    def __init__(
        self,
        llm: OpenAILLM,
        llm_settings_loader_service: BaseLLMSettingsLoaderService,
        llm_failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        OpenAIBasicManagedLLM.__init__(
            self, llm, llm_settings_loader_service, llm_failed_request_repository
        )
        OpenAIBatchManagedLLM.__init__(
            self, llm, llm_settings_loader_service, llm_failed_request_repository
        )
        OpenAIConcurrentManagedLLM.__init__(
            self, llm, llm_settings_loader_service, llm_failed_request_repository
        )
