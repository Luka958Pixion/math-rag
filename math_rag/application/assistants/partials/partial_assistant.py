from math_rag.application.base.assistants import BaseAssistant, BaseAssistantProtocol
from math_rag.application.base.inference import BaseLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialAssistant(
    BaseAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(
        self,
        llm: BaseLLM,
        settings_loader_service: BaseLLMSettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self.llm = llm
        self.settings_loader_service = settings_loader_service
        self.failed_request_repository = failed_request_repository

    async def assist(self, input: AssistantInputType) -> AssistantOutputType | None:
        request = self.encode_to_request(input)
        settings = self.settings_loader_service.load_llm_settings()
        result = await self.llm.generate(
            request,
            max_time=settings.max_time,
            max_num_retries=settings.max_num_retries,
        )

        if result.failed_request:
            await self.failed_request_repository.insert_one(result.failed_request)

            return None

        output = self.decode_from_response_list(result.response_list)

        return output
