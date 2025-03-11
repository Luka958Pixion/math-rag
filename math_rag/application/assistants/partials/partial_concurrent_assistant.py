from math_rag.application.base.assistants import BaseConcurrentAssistant
from math_rag.application.base.inference import BaseLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)

from .partial_assistant import PartialAssistant


class PartialConcurrentAssistant(
    PartialAssistant[AssistantInputType, AssistantOutputType],
    BaseConcurrentAssistant[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)
