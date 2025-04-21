from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseConcurrentAssistant,
)
from math_rag.application.base.inference import BaseConcurrentManagedLLM
from math_rag.application.models.inference import LLMConcurrentRequest
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialConcurrentAssistant(
    BaseConcurrentAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseConcurrentManagedLLM):
        self._llm = llm

    async def concurrent_assist(
        self,
        inputs: list[AssistantInputType],
    ) -> list[AssistantOutputType]:
        concurrent_request = LLMConcurrentRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        concurrent_result = await self._llm.concurrent_generate(concurrent_request)

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in concurrent_result.response_lists
        ]

        return outputs
