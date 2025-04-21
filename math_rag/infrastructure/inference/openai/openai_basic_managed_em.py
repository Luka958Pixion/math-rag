from math_rag.application.base.inference import BaseBasicEM, BaseBasicManagedEM
from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference import (
    EMRequest,
    EMResult,
)


class OpenAIBasicManagedEM(BaseBasicManagedEM):
    def __init__(
        self, em: BaseBasicEM, em_settings_loader_service: BaseEMSettingsLoaderService
    ):
        self._em = em
        self._em_settings_loader_service = em_settings_loader_service

    async def embed(self, request: EMRequest) -> EMResult:
        basic_settings = self._em_settings_loader_service.load_basic_settings(
            'openai', request.params.model
        )

        return await self._em.embed(
            request,
            max_time=basic_settings.max_time,
            max_num_retries=basic_settings.max_num_retries,
        )
