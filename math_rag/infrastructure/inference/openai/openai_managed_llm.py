from math_rag.application.base.inference import BaseLLM, BaseManagedLLM
from math_rag.application.models.inference import (
    LLMRequest,
    LLMResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIManagedLLM(BaseManagedLLM):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> LLMResult[LLMResponseType]:
        return await self.llm.generate(
            request,
            max_time=...,
            max_num_retries=...,  # TODO
        )
