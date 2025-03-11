from math_rag.application.base.assistants import BaseAssistant, BaseAssistantProtocol
from math_rag.application.base.inference import BaseLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialAssistant(
    BaseAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def assist(self, input: AssistantInputType) -> AssistantOutputType:
        request = self.encode_to_request(input)
        response_list = await self.llm.generate(request)
        output = self.decode_from_response(response_list)

        return output
