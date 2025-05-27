from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)

from .partial_basic_assistant import PartialBasicAssistant
from .partial_batch_assistant import PartialBatchAssistant
from .partial_concurrent_assistant import PartialConcurrentAssistant


class PartialAssistant(
    PartialBasicAssistant[AssistantInputType, AssistantOutputType],
    PartialBatchAssistant[AssistantInputType, AssistantOutputType],
    PartialConcurrentAssistant[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        PartialBasicAssistant.__init__(self, llm)
        PartialBatchAssistant.__init__(self, llm, scheduler)
        PartialConcurrentAssistant.__init__(self, llm)
