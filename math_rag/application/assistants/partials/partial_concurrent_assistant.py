from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseConcurrentAssistant,
)
from math_rag.application.base.inference import BaseLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialConcurrentAssistant(
    BaseConcurrentAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)
