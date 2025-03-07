from abc import ABC, abstractmethod
from typing import Generic, Type

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import (
    LLMRequest,
    LLMRequestBatch,
    LLMResponseList,
)
from math_rag.application.types import (
    AssistantInputType,
    AssistantOutputType,
    LLMResponseType,
)


class PartialAssistant(
    ABC, Generic[AssistantInputType, AssistantOutputType, LLMResponseType]
):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    @abstractmethod
    def to_request(self, input: AssistantInputType) -> LLMRequest[LLMResponseType]:
        pass

    @abstractmethod
    def from_response_list(
        self, response_list: LLMResponseList[LLMResponseType]
    ) -> AssistantOutputType:
        pass

    def to_request_batch(
        self, inputs: list[AssistantInputType]
    ) -> LLMRequestBatch[LLMResponseType]:
        request_batch = LLMRequestBatch(
            requests=[self.to_request(input) for input in inputs]
        )

        return request_batch

    async def assist(self, input: AssistantInputType) -> AssistantOutputType:
        request = self.to_request(input)
        response_list = await self.llm.generate(request)
        output = self.from_response_list(response_list)

        return output

    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: Type[LLMResponseType],
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
        batch_id = await self.llm.batch_generate_init(request_batch)

        return batch_id

    async def batch_assist_result(
        self,
        batch_id: str,
        response_type: Type[LLMResponseType],
    ) -> list[AssistantOutputType] | None:
        response_batch = await self.llm.batch_generate_result(batch_id, response_type)

        if response_batch is None:
            return

        outputs = [
            self.from_response_list(response_list)
            for response_list in response_batch.response_lists
        ]

        return outputs
