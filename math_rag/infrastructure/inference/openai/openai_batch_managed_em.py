from uuid import UUID

from math_rag.application.base.inference import BaseBatchEM, BaseBatchManagedEM
from math_rag.application.models.inference import EMBatchRequest, EMBatchResult


class OpenAIBatchManagedEM(BaseBatchManagedEM):
    def __init__(self, em: BaseBatchEM):
        self.em = em

    async def batch_embed(self, batch_request: EMBatchRequest) -> EMBatchResult:
        return await self.em.batch_embed(
            batch_request,
            poll_interval=...,
            max_num_retries=...,  # TODO
        )

    async def batch_embed_init(self, batch_request: EMBatchRequest) -> str:
        return await self.em.batch_embed_init(batch_request)

    async def batch_embed_result(
        self, batch_id: str, batch_request_id: UUID
    ) -> EMBatchResult | None:
        return await self.em.batch_embed_result(batch_id, batch_request_id)
