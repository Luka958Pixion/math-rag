from math_rag.application.base.inference import (
    BaseConcurrentEM,
    BaseConcurrentManagedEM,
)
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import (
    EMConcurrentRequest,
    EMConcurrentResult,
)


class OpenAIConcurrentManagedEM(BaseConcurrentManagedEM):
    def __init__(
        self,
        em: BaseConcurrentEM,
        em_settings_loader_service: BaseEMSettingsLoaderService,
    ):
        self._em = em
        self._em_settings_loader_service = em_settings_loader_service

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

        return await self._em.concurrent_embed(
            concurrent_request,
            max_requests_per_minute=concurrent_settings.max_requests_per_minute,
            max_tokens_per_minute=concurrent_settings.max_tokens_per_minute,
            max_num_retries=concurrent_settings.max_num_retries,
        )
