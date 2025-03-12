from math_rag.application.base.inference import BaseUnifiedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.services import SettingsLoaderService
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
        settings_loader_service: SettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        super().__init__(llm, settings_loader_service, failed_request_repository)
