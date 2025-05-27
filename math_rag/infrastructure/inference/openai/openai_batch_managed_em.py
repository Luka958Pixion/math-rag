from uuid import UUID

from math_rag.application.base.inference import BaseBatchManagedEM
from math_rag.application.base.repositories.documents import (
    BaseEMFailedRequestRepository,
)
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import EMBatchRequest, EMBatchResult
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator

from .openai_batch_em import OpenAIBatchEM


class OpenAIBatchManagedEM(BaseBatchManagedEM):
    def __init__(
        self,
        em: OpenAIBatchEM,
        em_settings_loader_service: BaseEMSettingsLoaderService,
        em_failed_request_repository: BaseEMFailedRequestRepository,
    ):
        self._em = em
        self._em_settings_loader_service = em_settings_loader_service
        self._em_failed_request_repository = em_failed_request_repository

    async def batch_embed(self, batch_request: EMBatchRequest) -> EMBatchResult:
        if not batch_request.requests:
            raise ValueError(f'Batch request {batch_request.id} is empty')

        model = batch_request.requests[0].params.model
        OpenAIModelNameValidator.validate(model)

        batch_settings = self._em_settings_loader_service.load_batch_settings('openai', model)

        if batch_settings.poll_interval is None:
            raise ValueError('poll_interval can not be None')

        elif batch_settings.max_tokens_per_day is None:
            raise ValueError('max_num_retries can not be None')

        elif batch_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        batch_result = await self._em.batch_embed(
            batch_request,
            poll_interval=batch_settings.poll_interval,
            max_tokens_per_day=batch_settings.max_tokens_per_day,
            max_input_file_size=batch_settings.max_input_file_size,
            max_num_retries=batch_settings.max_num_retries,
        )

        if batch_result.failed_requests:
            await self._em_failed_request_repository.insert_many(batch_result.failed_requests)

        return batch_result

    async def batch_embed_init(self, batch_request: EMBatchRequest) -> str:
        return await self._em.batch_embed_init(batch_request)

    async def batch_embed_result(
        self, batch_id: str, batch_request_id: UUID
    ) -> EMBatchResult | None:
        return await self._em.batch_embed_result(batch_id, batch_request_id)
