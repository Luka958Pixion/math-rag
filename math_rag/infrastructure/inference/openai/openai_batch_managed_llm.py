from uuid import UUID

from math_rag.application.base.inference import BaseBatchLLM, BaseBatchManagedLLM
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIBatchManagedLLM(BaseBatchManagedLLM):
    def __init__(self, llm: BaseBatchLLM):
        self.llm = llm

    async def batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType]:
        return await self.llm.batch_generate(
            batch_request,
            response_type,
            poll_interval=...,
            max_num_retries=...,  # TODO
        )

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        return await self.llm.batch_generate_init(batch_request)

    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType] | None:
        return await self.llm.batch_generate_result(
            batch_id, batch_request_id, response_type
        )
