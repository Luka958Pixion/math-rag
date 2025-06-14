from uuid import UUID

from math_rag.application.base.inference import BaseManagedLLM
from math_rag.application.enums.inference import LLMInferenceProvider
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMConcurrentRequest,
    LLMConcurrentResult,
    LLMRequest,
    LLMResult,
)
from math_rag.application.types.inference import LLMResponseType


class ManagedLLMRouter(BaseManagedLLM):
    def __init__(
        self, inference_provider_to_managed_llm: dict[LLMInferenceProvider, BaseManagedLLM]
    ):
        self.inference_provider_to_managed_llm = inference_provider_to_managed_llm

    def _llm(
        self,
        request: LLMRequest[LLMResponseType]
        | LLMBatchRequest[LLMResponseType]
        | LLMConcurrentRequest[LLMResponseType],
    ) -> BaseManagedLLM:
        # get inference provider
        if isinstance(request, LLMRequest):
            inference_provider = request.params.inference_provider

        elif isinstance(request, LLMBatchRequest):
            if not request.requests:
                raise ValueError(f'Batch request {request.id} is empty')

            inference_provider = request.requests[0].params.inference_provider

        elif isinstance(request, LLMConcurrentRequest):
            if not request.requests:
                raise ValueError(f'Batch request {request.id} is empty')

            inference_provider = request.requests[0].params.inference_provider

        else:
            raise TypeError(f'Unknown LLM request type: {type(request)}')

        # get model
        llm = self.inference_provider_to_managed_llm.get(inference_provider)

        if llm is None:
            raise ValueError(f'LLM inference provider {inference_provider} is not available')

        return llm

    async def generate(self, request: LLMRequest[LLMResponseType]) -> LLMResult[LLMResponseType]:
        llm = self._llm(request)

        return await llm.generate(request)

    async def batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType]:
        llm = self._llm(batch_request)

        return await llm.batch_generate(batch_request, response_type)

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        self.llm = self._llm(batch_request)

        return await self.llm.batch_generate_init(batch_request)

    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType] | None:
        batch_result = await self.llm.batch_generate_result(
            batch_id, batch_request_id, response_type
        )
        self.llm = None

        return batch_result

    async def concurrent_generate(
        self, concurrent_request: LLMConcurrentRequest[LLMResponseType]
    ) -> LLMConcurrentResult[LLMResponseType]:
        llm = self._llm(concurrent_request)

        return await llm.concurrent_generate(concurrent_request)
