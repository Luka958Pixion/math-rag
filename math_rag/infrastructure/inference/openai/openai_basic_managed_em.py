from math_rag.application.base.inference import BaseBasicManagedEM
from math_rag.application.base.repositories.documents import (
    BaseEMFailedRequestRepository,
)
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import (
    EMRequest,
    EMResult,
)

from .openai_basic_em import OpenAIBasicEM


class OpenAIBasicManagedEM(BaseBasicManagedEM):
    def __init__(
        self,
        em: OpenAIBasicEM,
        em_settings_loader_service: BaseEMSettingsLoaderService,
        em_failed_request_repository: BaseEMFailedRequestRepository,
    ):
        self._em = em
        self._em_settings_loader_service = em_settings_loader_service
        self._em_failed_request_repository = em_failed_request_repository

    async def embed(self, request: EMRequest) -> EMResult:
        basic_settings = self._em_settings_loader_service.load_basic_settings(
            'openai', request.params.model
        )

        if basic_settings.max_time is None:
            raise ValueError('max_time can not be None')

        elif basic_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        result = await self._em.embed(
            request,
            max_time=basic_settings.max_time,
            max_num_retries=basic_settings.max_num_retries,
        )

        if result.failed_request:
            await self._em_failed_request_repository.insert_one(result.failed_request)

        return result
