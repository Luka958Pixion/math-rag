from math_rag.application.base.inference import BaseBasicLLM, BaseBasicManagedLLM
from math_rag.application.models.inference import (
    LLMRequest,
    LLMResult,
)
from math_rag.application.types.inference import LLMResponseType


class OpenAIBasicManagedLLM(BaseBasicManagedLLM):
    def __init__(self, llm: BaseBasicLLM):
        self.llm = llm

    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> LLMResult[LLMResponseType]:
        return await self.llm.generate(
            request,
            max_time=...,
            max_num_retries=...,  # TODO
        )
