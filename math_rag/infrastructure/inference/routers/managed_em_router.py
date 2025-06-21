from uuid import UUID

from math_rag.application.base.inference import BaseManagedEM
from math_rag.application.enums.inference import EMInferenceProvider
from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchResult,
    EMConcurrentRequest,
    EMConcurrentResult,
    EMRequest,
    EMResult,
)


class ManagedEMRouter(BaseManagedEM):
    def __init__(self, inference_provider_to_managed_em: dict[EMInferenceProvider, BaseManagedEM]):
        self.inference_provider_to_managed_em = inference_provider_to_managed_em

    def _em(self, request: EMRequest | EMBatchRequest | EMConcurrentRequest) -> BaseManagedEM:
        # get inference provider
        if isinstance(request, EMRequest):
            inference_provider = request.router_params.inference_provider

        elif isinstance(request, EMBatchRequest):
            if not request.requests:
                raise ValueError(f'Batch request {request.id} is empty')

            inference_provider = request.requests[0].router_params.inference_provider

        elif isinstance(request, EMConcurrentRequest):
            if not request.requests:
                raise ValueError(f'Batch request {request.id} is empty')

            inference_provider = request.requests[0].router_params.inference_provider

        else:
            raise TypeError(f'Unknown EM request type: {type(request)}')

        # get model
        em = self.inference_provider_to_managed_em.get(inference_provider)

        if em is None:
            raise ValueError(f'EM inference provider {inference_provider} is not available')

        return em

    async def embed(self, request: EMRequest) -> EMResult:
        em = self._em(request)

        return await em.embed(request)

    async def batch_embed(self, batch_request: EMBatchRequest) -> EMBatchResult:
        em = self._em(batch_request)

        return await em.batch_embed(batch_request)

    async def batch_embed_init(self, batch_request: EMBatchRequest) -> str:
        self.em = self._em(batch_request)

        return await self.em.batch_embed_init(batch_request)

    async def batch_embed_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> EMBatchResult | None:
        batch_result = await self.em.batch_embed_result(batch_id, batch_request_id)
        self.em = None

        return batch_result

    async def concurrent_embed(self, concurrent_request: EMConcurrentRequest) -> EMConcurrentResult:
        em = self._em(concurrent_request)

        return await em.concurrent_embed(concurrent_request)
