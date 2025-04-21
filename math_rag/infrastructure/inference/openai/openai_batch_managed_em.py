from uuid import UUID

from math_rag.application.base.inference import BaseBatchEM, BaseBatchManagedEM
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import EMBatchRequest, EMBatchResult


class OpenAIBatchManagedEM(BaseBatchManagedEM):
    def __init__(
        self, em: BaseBatchEM, em_settings_loader_service: BaseEMSettingsLoaderService
    ):
        self._em = em
        self._em_settings_loader_service = em_settings_loader_service

    async def batch_embed(self, batch_request: EMBatchRequest) -> EMBatchResult:
        batch_settings = self._em_settings_loader_service.load_batch_settings(
            'openai', batch_request.requests[0].params.model
        )

        return await self._em.batch_embed(
            batch_request,
            poll_interval=batch_settings.poll_interval,
            max_num_retries=batch_settings.max_num_retries,
        )

    async def batch_embed_init(self, batch_request: EMBatchRequest) -> str:
        return await self._em.batch_embed_init(batch_request)

    async def batch_embed_result(
        self, batch_id: str, batch_request_id: UUID
    ) -> EMBatchResult | None:
        return await self._em.batch_embed_result(batch_id, batch_request_id)
