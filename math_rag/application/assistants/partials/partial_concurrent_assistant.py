from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseConcurrentAssistant,
)
from math_rag.application.base.inference import BaseConcurrentLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseSettingsLoaderService
from math_rag.application.models.inference import LLMRequestConcurrent
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialConcurrentAssistant(
    BaseConcurrentAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(
        self,
        llm: BaseConcurrentLLM,
        settings_loader_service: BaseSettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self.llm = llm
        self.settings_loader_service = settings_loader_service
        self.failed_request_repository = failed_request_repository

    async def concurrent_assist(
        self,
        inputs: list[AssistantInputType],
    ) -> list[AssistantOutputType]:
        request_concurrent = LLMRequestConcurrent(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        settings = self.settings_loader_service.load_concurrent_llm_settings()
        response_bundle = await self.llm.concurrent_generate(
            request_concurrent,
            max_requests_per_minute=settings.max_requests_per_minute,
            max_tokens_per_minute=settings.max_tokens_per_minute,
            max_num_retries=settings.max_num_retries,
        )

        if response_bundle.failed_requests:
            await self.failed_request_repository.insert_many(
                response_bundle.failed_requests
            )

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in response_bundle.response_lists
        ]

        return outputs
