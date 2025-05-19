from typing import cast

from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseBasicAssistant,
)
from math_rag.application.base.inference import BaseBasicManagedLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)
from math_rag.shared.utils import TypeUtil


class PartialBasicAssistant(
    BaseBasicAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseBasicManagedLLM):
        self._llm = llm

        args = TypeUtil.get_type_args(self.__class__)
        self._response_type = cast(type[AssistantOutputType], args[0][1])

    async def assist(self, input: AssistantInputType) -> AssistantOutputType | None:
        request = self.encode_to_request(input)
        result = await self._llm.generate(request)

        if result.failed_request:
            return None

        # map BoundAssistantOutput to AssistantOutput
        for response in result.response_list.responses:
            content_dict = response.content.model_dump()
            response.content = self._response_type(**content_dict)

        output = self.decode_from_response_list(result.response_list)

        return output
