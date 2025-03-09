from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMRequest,
    LLMRequestBatch,
    LLMResponseBatch,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType


class BaseLLM(ABC):
    @abstractmethod
    async def generate(
        self, request: LLMRequest[LLMResponseType]
    ) -> LLMResponseList[LLMResponseType]:
        pass

    @abstractmethod
    async def batch_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        poll_interval: float,
    ) -> LLMResponseBatch[LLMResponseType]:
        pass

    @abstractmethod
    async def batch_generate_retry(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        poll_interval: float,
        num_retries: int,
    ) -> LLMResponseBatch[LLMResponseType]:
        pass

    @abstractmethod
    async def batch_generate_init(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> str:
        pass

    @abstractmethod
    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMResponseBatch[LLMResponseType] | None:
        pass
