from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
)
from math_rag.application.types.inference import LLMResponseType


class BaseBatchLLM(ABC):
    @abstractmethod
    async def batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> LLMBatchResult[LLMResponseType]:
        pass

    @abstractmethod
    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        pass

    @abstractmethod
    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType] | None:
        pass
