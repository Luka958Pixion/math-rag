from math_rag.application.base.inference import BaseConcurrentManagedEM
from math_rag.application.base.repositories.documents import (
    BaseEMFailedRequestRepository,
)
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import (
    EMConcurrentRequest,
    EMConcurrentResult,
)

from .openai_concurrent_em import OpenAIConcurrentEM


class OpenAIConcurrentManagedEM(BaseConcurrentManagedEM):
    def __init__(
        self,
        em: OpenAIConcurrentEM,
        em_settings_loader_service: BaseEMSettingsLoaderService,
        em_failed_request_repository: BaseEMFailedRequestRepository,
    ):
        self._em = em
        self._em_settings_loader_service = em_settings_loader_service
        self._em_failed_request_repository = em_failed_request_repository

    async def concurrent_embed(
        self, concurrent_request: EMConcurrentRequest
    ) -> EMConcurrentResult:
        concurrent_settings = self._em_settings_loader_service.load_concurrent_settings(
            'openai', concurrent_request.requests[0].params.model
        )

        if concurrent_settings.max_requests_per_minute is None:
            raise ValueError('max_requests_per_minute can not be None')

        elif concurrent_settings.max_tokens_per_minute is None:
            raise ValueError('max_tokens_per_minute can not be None')

        elif concurrent_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        concurrent_result = await self._em.concurrent_embed(
            concurrent_request,
            max_requests_per_minute=concurrent_settings.max_requests_per_minute,
            max_tokens_per_minute=concurrent_settings.max_tokens_per_minute,
            max_num_retries=concurrent_settings.max_num_retries,
        )

        if concurrent_result.failed_requests:
            await self._em_failed_request_repository.insert_many(
                concurrent_result.failed_requests
            )

        return concurrent_result
