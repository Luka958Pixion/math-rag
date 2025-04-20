from math_rag.application.base.inference import (
    BaseConcurrentEM,
    BaseConcurrentManagedEM,
)
from math_rag.application.models.inference import (
    EMConcurrentRequest,
    EMConcurrentResult,
)


class OpenAIConcurrentManagedEM(BaseConcurrentManagedEM):
    def __init__(self, em: BaseConcurrentEM):
        self.em = em

    async def concurrent_embed(
        self, concurrent_request: EMConcurrentRequest
    ) -> EMConcurrentResult:
        return await self.em.concurrent_embed(
            concurrent_request,
            max_requests_per_minute=...,
            max_tokens_per_minute=...,
            max_num_retries=...,  # TODO
        )
