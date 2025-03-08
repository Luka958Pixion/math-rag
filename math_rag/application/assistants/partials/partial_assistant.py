from math_rag.application.base.assistants import BaseAssistant
from math_rag.application.base.inference import BaseLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialAssistant(BaseAssistant[AssistantInputType, AssistantOutputType]):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def assist(self, input: AssistantInputType) -> AssistantOutputType:
        request = self.to_request(input)
        response_list = await self.llm.generate(request)
        output = self.from_response_list(response_list)

        return output
