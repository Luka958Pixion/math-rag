from math_rag.application.base.inference import BaseUnifiedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseSettingsLoaderService
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)

from .partial_assistant import PartialAssistant
from .partial_batch_assistant import PartialBatchAssistant
from .partial_concurrent_assistant import PartialConcurrentAssistant


class PartialUnifiedAssistant(
    PartialAssistant[AssistantInputType, AssistantOutputType],
    PartialBatchAssistant[AssistantInputType, AssistantOutputType],
    PartialConcurrentAssistant[AssistantInputType, AssistantOutputType],
):
    def __init__(
        self,
        llm: BaseUnifiedLLM,
        settings_loader_service: BaseSettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        PartialAssistant.__init__(
            self, llm, settings_loader_service, failed_request_repository
        )
        PartialBatchAssistant.__init__(
            self, llm, settings_loader_service, failed_request_repository
        )
        PartialConcurrentAssistant.__init__(
            self, llm, settings_loader_service, failed_request_repository
        )
