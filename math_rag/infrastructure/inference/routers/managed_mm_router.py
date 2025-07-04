from math_rag.application.base.inference import BaseManagedMM
from math_rag.application.enums.inference import MMInferenceProvider
from math_rag.application.models.inference import (
    MMConcurrentRequest,
    MMConcurrentResult,
    MMRequest,
    MMResult,
)


class ManagedMMRouter(BaseManagedMM):
    def __init__(self, inference_provider_to_managed_mm: dict[MMInferenceProvider, BaseManagedMM]):
        self.inference_provider_to_managed_mm = inference_provider_to_managed_mm

    def _mm(self, request: MMRequest | MMConcurrentRequest) -> BaseManagedMM:
        # get inference provider
        if isinstance(request, MMRequest):
            inference_provider = request.router_params.inference_provider

        elif isinstance(request, MMConcurrentRequest):
            if not request.requests:
                raise ValueError(f'Batch request {request.id} is empty')

            inference_provider = request.requests[0].router_params.inference_provider

        else:
            raise TypeError(f'Unknown MM request type: {type(request)}')

        # get model
        mm = self.inference_provider_to_managed_mm.get(inference_provider)

        if mm is None:
            raise ValueError(f'MM inference provider {inference_provider} is not available')

        return mm

    async def moderate(self, request: MMRequest) -> MMResult:
        mm = self._mm(request)

        return await mm.moderate(request)

    async def concurrent_moderate(
        self, concurrent_request: MMConcurrentRequest
    ) -> MMConcurrentResult:
        mm = self._mm(concurrent_request)

        return await mm.concurrent_moderate(concurrent_request)
