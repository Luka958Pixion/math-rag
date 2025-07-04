from math_rag.application.base.inference import BaseBasicManagedMM
from math_rag.application.base.repositories.documents import BaseMMFailedRequestRepository
from math_rag.application.base.services import BaseMMSettingsLoaderService
from math_rag.application.models.inference import MMRequest, MMResult
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator

from .openai_basic_mm import OpenAIBasicMM


class OpenAIBasicManagedMM(BaseBasicManagedMM):
    def __init__(
        self,
        mm: OpenAIBasicMM,
        mm_settings_loader_service: BaseMMSettingsLoaderService,
        mm_failed_request_repository: BaseMMFailedRequestRepository,
    ):
        self._mm = mm
        self._mm_settings_loader_service = mm_settings_loader_service
        self._mm_failed_request_repository = mm_failed_request_repository

    async def moderate(self, request: MMRequest) -> MMResult:
        OpenAIModelNameValidator.validate(request.params.model)

        basic_settings = self._mm_settings_loader_service.load_basic_settings(
            'openai', request.params.model
        )

        if basic_settings.max_time is None:
            raise ValueError('max_time can not be None')

        elif basic_settings.max_num_retries is None:
            raise ValueError('max_num_retries can not be None')

        result = await self._mm.moderate(
            request,
            max_time=basic_settings.max_time,
            max_num_retries=basic_settings.max_num_retries,
        )

        if result.failed_request:
            await self._mm_failed_request_repository.insert_one(result.failed_request)

        return result
