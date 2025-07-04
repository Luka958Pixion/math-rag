from math_rag.application.base.repositories.documents import BaseEMFailedRequestRepository
from math_rag.application.base.services import BaseEMSettingsLoaderService

from .openai_basic_managed_em import OpenAIBasicManagedEM
from .openai_batch_managed_em import OpenAIBatchManagedEM
from .openai_concurrent_managed_em import OpenAIConcurrentManagedEM
from .openai_em import OpenAIEM


class OpenAIManagedEM(OpenAIBasicManagedEM, OpenAIBatchManagedEM, OpenAIConcurrentManagedEM):
    def __init__(
        self,
        em: OpenAIEM,
        em_settings_loader_service: BaseEMSettingsLoaderService,
        em_failed_request_repository: BaseEMFailedRequestRepository,
    ):
        OpenAIBasicManagedEM.__init__(
            self, em, em_settings_loader_service, em_failed_request_repository
        )
        OpenAIBatchManagedEM.__init__(
            self, em, em_settings_loader_service, em_failed_request_repository
        )
        OpenAIConcurrentManagedEM.__init__(
            self, em, em_settings_loader_service, em_failed_request_repository
        )
