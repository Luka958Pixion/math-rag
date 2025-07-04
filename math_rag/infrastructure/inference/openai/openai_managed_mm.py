from math_rag.application.base.repositories.documents import BaseMMFailedRequestRepository
from math_rag.application.base.services import BaseMMSettingsLoaderService

from .openai_basic_managed_mm import OpenAIBasicManagedMM
from .openai_concurrent_managed_mm import OpenAIConcurrentManagedMM
from .openai_mm import OpenAIMM


class OpenAIManagedMM(OpenAIBasicManagedMM, OpenAIConcurrentManagedMM):
    def __init__(
        self,
        mm: OpenAIMM,
        mm_settings_loader_service: BaseMMSettingsLoaderService,
        mm_failed_request_repository: BaseMMFailedRequestRepository,
    ):
        OpenAIBasicManagedMM.__init__(
            self, mm, mm_settings_loader_service, mm_failed_request_repository
        )
        OpenAIConcurrentManagedMM.__init__(
            self, mm, mm_settings_loader_service, mm_failed_request_repository
        )
