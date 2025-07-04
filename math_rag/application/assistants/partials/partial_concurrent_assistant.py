from typing import cast

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
from math_rag.shared.utils import TypeUtil


class PartialConcurrentAssistant(
    BaseConcurrentAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseConcurrentManagedLLM):
        self._llm = llm

        args = TypeUtil.get_type_args(self.__class__)
        self._response_type = cast(type[AssistantOutputType], args[0][1])

    async def concurrent_assist(
        self,
        inputs: list[AssistantInputType],
    ) -> list[AssistantOutputType]:
        concurrent_request = LLMConcurrentRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        concurrent_result = await self._llm.concurrent_generate(concurrent_request)

        # map BoundAssistantOutput to AssistantOutput
        for response_list in concurrent_result.response_lists:
            for response in response_list.responses:
                content_dict = response.content.model_dump(exclude_unset=True)
                response.content = self._response_type(**content_dict)

        return [
            self.decode_from_response_list(response_list)
            for response_list in concurrent_result.response_lists
        ]
