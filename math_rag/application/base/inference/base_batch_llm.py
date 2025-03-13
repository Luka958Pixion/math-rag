from abc import ABC, abstractmethod

from math_rag.application.models.inference import (
    LLMBatchResult,
    LLMRequestBatch,
)
from math_rag.application.types.inference import LLMResponseType


class BaseBatchLLM(ABC):
    @abstractmethod
    async def batch_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> LLMBatchResult[LLMResponseType]:
        pass

    @abstractmethod
    async def batch_generate_init(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
    ) -> str:
        pass

    @abstractmethod
    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMBatchResult[LLMResponseType] | None:
        pass
