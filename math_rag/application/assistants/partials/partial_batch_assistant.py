from typing import cast

from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseBatchAssistant,
    BaseBatchAssistantProtocol,
)
from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import LLMRequestBatch
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)
from math_rag.shared.utils import TypeUtil


class PartialBatchAssistant(
    BaseBatchAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
    BaseBatchAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)

        args = TypeUtil.get_type_args(self.__class__)
        self.response_type = cast(type[AssistantOutputType], args[0][1])

    def encode_to_request_batch(
        self, inputs: list[AssistantInputType]
    ) -> LLMRequestBatch[AssistantOutputType]:
        request_batch = LLMRequestBatch(
            requests=[self.encode_to_request(input) for input in inputs]
        )

        return request_batch

    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: type[AssistantOutputType],
        poll_interval: float,
        num_retries: int,
    ) -> tuple[list[AssistantInputType], list[AssistantOutputType]]:
        request_batch = self.encode_to_request_batch(inputs)
        response_batch = await self.llm.batch_generate_retry(
            request_batch, response_type, poll_interval, num_retries
        )
        outputs = [
            self.from_response_list(response_list)
            for response_list in response_batch.response_lists
        ]
        num_completed = len(response_batch.response_lists)
        num_total = len(inputs)
        num_remaining = num_total - num_completed
        remaining_assistant_requests = inputs[-num_remaining:]

        return remaining_assistant_requests, outputs

    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        request_batch = self.encode_to_request_batch(inputs)
        batch_id = await self.llm.batch_generate_init(request_batch, self.response_type)

        return batch_id

    async def batch_assist_result(
        self,
        batch_id: str,
    ) -> list[AssistantOutputType] | None:
        response_batch = await self.llm.batch_generate_result(
            batch_id, self.response_type
        )

        if response_batch is None:
            return

        outputs = [
            self.from_response_list(response_list)
            for response_list in response_batch.response_lists
        ]

        return outputs
