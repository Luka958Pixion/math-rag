from math_rag.application.base.assistants import BaseAssistant, BaseAssistantProtocol
from math_rag.application.base.inference import BaseLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialAssistant(
    BaseAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(
        self, llm: BaseLLM, failed_request_repository: BaseLLMFailedRequestRepository
    ):
        self.llm = llm
        self.failed_request_repository = failed_request_repository

    async def assist(self, input: AssistantInputType) -> AssistantOutputType | None:
        request = self.encode_to_request(input)
        response_bundle = await self.llm.generate(request)

        if response_bundle.failed_request:
            await self.failed_request_repository.insert_one(
                response_bundle.failed_request
            )

            return None

        output = self.decode_from_response_list(response_bundle.response_list)

        return output
