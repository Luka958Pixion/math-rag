from typing import cast
from uuid import UUID

from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseBatchAssistant,
)
from math_rag.application.base.inference import BaseBatchManagedLLM
from math_rag.application.models.inference import LLMBatchRequest
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)
from math_rag.shared.utils import TypeUtil


class PartialBatchAssistant(
    BaseBatchAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseBatchManagedLLM):
        self._llm = llm

        args = TypeUtil.get_type_args(self.__class__)
        self._response_type = cast(type[AssistantOutputType], args[0][1])

    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: type[AssistantOutputType],
    ) -> list[AssistantOutputType]:
        requests = [self.encode_to_request(input) for input in inputs]
        batch_request = LLMBatchRequest(requests=requests)
        batch_result = await self._llm.batch_generate(batch_request, response_type)

        # map BoundAssistantOutput to AssistantOutput
        for response_list in batch_result.response_lists:
            for response in response_list.responses:
                content_dict = response.content.model_dump(exclude_unset=True)
                response.content = self._response_type(**content_dict)

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in batch_result.response_lists
        ]

        return outputs

    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        requests = [self.encode_to_request(input) for input in inputs]
        batch_request = LLMBatchRequest(requests=requests)
        batch_id = await self._llm.batch_generate_init(batch_request)

        return batch_id

    async def batch_assist_result(
        self, batch_id: str, batch_request_id: UUID
    ) -> list[AssistantOutputType] | None:
        batch_result = await self._llm.batch_generate_result(
            batch_id,
            batch_request_id,
            self._response_type,
        )

        if batch_result is None:
            return

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in batch_result.response_lists
        ]

        return outputs
