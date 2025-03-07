from typing import Callable, Generic, Type, TypeVar

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMRequestBatch,
    LLMResponse,
)
from math_rag.application.types import LLMResponseType


AssistantInputType = TypeVar('AssistantRequestType')
AssistantOutputType = TypeVar('AssistantResponseType')


class BatchGeneratorService(Generic[AssistantInputType, AssistantOutputType]):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    def create_request_batch(
        self,
        assistant_inputs: list[AssistantInputType],
        create_request_callback: Callable[
            [AssistantInputType], LLMRequest[LLMResponseType]
        ],
    ) -> LLMRequestBatch[LLMResponseType]:
        request_batch = LLMRequestBatch(
            requests=[
                create_request_callback(assistant_input)
                for assistant_input in assistant_inputs
            ]
        )

        return request_batch

    async def batch_generate(
        self,
        assistant_inputs: list[AssistantInputType],
        create_request_callback: Callable[
            [AssistantInputType], LLMRequest[LLMResponseType]
        ],
        assistant_output_mapping: Callable[
            [list[LLMResponse[LLMResponseType]]], AssistantOutputType
        ],
        response_type: Type[LLMResponseType],
        delay: float,
        num_retries: int,
    ) -> tuple[list[str], list[AssistantOutputType]]:
        request_batch = self.create_request_batch(
            assistant_inputs, create_request_callback
        )
        response_batch = await self.llm.batch_generate_retry(
            request_batch, response_type, delay, num_retries
        )
        outputs = [
            assistant_output_mapping(responses)
            for responses in response_batch.nested_responses
        ]
        num_completed = len(response_batch.nested_responses)
        num_total = len(assistant_inputs)
        num_remaining = num_total - num_completed
        remaining_assistant_requests = assistant_inputs[-num_remaining:]

        return remaining_assistant_requests, outputs

    async def batch_generate_init(
        self, assistant_inputs: list[AssistantInputType]
    ) -> AssistantOutputType:
        request_batch = self.create_request_batch(assistant_inputs)
        batch_id = await self.llm.batch_generate_init(request_batch)

        return batch_id

    async def batch_generate_result(
        self,
        batch_id: str,
        response_type: Type[LLMResponseType],
        assistant_output_mapping: Callable[
            [list[LLMResponse[LLMResponseType]]], AssistantOutputType
        ],
    ) -> list[AssistantOutputType] | None:
        response_batch = await self.llm.batch_generate_result(batch_id, response_type)

        if response_batch is None:
            return

        outputs = [
            assistant_output_mapping(responses)
            for responses in response_batch.nested_responses
        ]

        return outputs
