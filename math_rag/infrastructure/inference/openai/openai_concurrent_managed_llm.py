from math_rag.application.base.inference import (
    BaseConcurrentLLM,
    BaseConcurrentManagedLLM,
)
from math_rag.application.models.inference import (
    LLMConcurrentRequest,
    LLMConcurrentResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIConcurrentManagedLLM(BaseConcurrentManagedLLM):
    def __init__(self, llm: BaseConcurrentLLM):
        self.llm = llm

    async def concurrent_generate(
        self, concurrent_request: LLMConcurrentRequest[LLMResponseType]
    ) -> LLMConcurrentResult[LLMResponseType]:
        return await self.llm.concurrent_generate(
            concurrent_request,
            max_requests_per_minute=...,
            max_tokens_per_minute=...,
            max_num_retries=...,  # TODO
        )
