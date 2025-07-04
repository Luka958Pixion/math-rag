from math_rag.application.base.inference import BaseConcurrentManagedMM
from math_rag.application.base.repositories.documents import BaseMMFailedRequestRepository
from math_rag.application.base.services import BaseMMSettingsLoaderService
from math_rag.application.models.inference import MMConcurrentRequest, MMConcurrentResult
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator

from .openai_concurrent_mm import OpenAIConcurrentMM


class OpenAIConcurrentManagedMM(BaseConcurrentManagedMM):
    def __init__(
        self,
        mm: OpenAIConcurrentMM,
        mm_settings_loader_service: BaseMMSettingsLoaderService,
        mm_failed_request_repository: BaseMMFailedRequestRepository,
    ):
        self._mm = mm
        self._mm_settings_loader_service = mm_settings_loader_service
        self._mm_failed_request_repository = mm_failed_request_repository

    async def concurrent_moderate(
        self, concurrent_request: MMConcurrentRequest
    ) -> MMConcurrentResult:
        if not concurrent_request.requests:
            raise ValueError(f'Concurrent request {concurrent_request.id} is empty')

        model = concurrent_request.requests[0].params.model
        OpenAIModelNameValidator.validate(model)

        concurrent_settings = self._mm_settings_loader_service.load_concurrent_settings(
            'openai', model
        )

        if concurrent_settings.max_requests_per_minute is None:
            raise ValueError('max_requests_per_minute can not be None')

        elif concurrent_settings.max_tokens_per_minute is None:
            raise ValueError('max_tokens_per_minute can not be None')

        elif concurrent_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        concurrent_result = await self._mm.concurrent_moderate(
            concurrent_request,
            max_requests_per_minute=concurrent_settings.max_requests_per_minute,
            max_tokens_per_minute=concurrent_settings.max_tokens_per_minute,
            max_num_retries=concurrent_settings.max_num_retries,
        )

        if concurrent_result.failed_requests:
            await self._mm_failed_request_repository.insert_many(concurrent_result.failed_requests)

        return concurrent_result
