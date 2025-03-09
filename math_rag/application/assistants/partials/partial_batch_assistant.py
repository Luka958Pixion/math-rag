from typing import cast

from math_rag.application.base.assistants import BaseBatchAssistant
from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import LLMRequestBatch
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)
from math_rag.shared.utils import TypeArgExtractorUtil

from .partial_assistant import PartialAssistant


class PartialBatchAssistant(
    PartialAssistant[AssistantInputType, AssistantOutputType],
    BaseBatchAssistant[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)

        args = TypeArgExtractorUtil.extract(self.__class__)
        self.response_type = cast(type[AssistantOutputType], args[0][1])

    def to_request_batch(
        self, inputs: list[AssistantInputType]
    ) -> LLMRequestBatch[AssistantOutputType]:
        request_batch = LLMRequestBatch(
            requests=[self.to_request(input) for input in inputs]
        )

        return request_batch

    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: type[AssistantOutputType],
        delay: float,
        num_retries: int,
    ) -> tuple[list[AssistantInputType], list[AssistantOutputType]]:
        request_batch = self.to_request_batch(inputs)
        response_batch = await self.llm.batch_generate_retry(
            request_batch, response_type, delay, num_retries
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
        request_batch = self.to_request_batch(inputs)
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
