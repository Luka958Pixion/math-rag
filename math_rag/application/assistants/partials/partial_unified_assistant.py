from math_rag.application.base.inference import BaseLLM
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
    def __init__(self, llm: BaseLLM):
        PartialAssistant.__init__(self, llm)
        PartialBatchAssistant.__init__(self, llm)
        PartialConcurrentAssistant.__init__(self, llm)
