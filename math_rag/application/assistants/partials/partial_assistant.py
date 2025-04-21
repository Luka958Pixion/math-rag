from math_rag.application.base.assistants import BaseAssistant, BaseAssistantProtocol
from math_rag.application.base.inference import BaseBasicManagedLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialAssistant(
    BaseAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseBasicManagedLLM):
        self._llm = llm

    async def assist(self, input: AssistantInputType) -> AssistantOutputType | None:
        request = self.encode_to_request(input)
        result = await self._llm.generate(request)
        output = self.decode_from_response_list(result.response_list)

        return output
