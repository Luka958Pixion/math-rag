from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.base.inference import BaseLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class BaseAssistant(ABC, Generic[AssistantInputType, AssistantOutputType]):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    @abstractmethod
    async def assist(self, input: AssistantInputType) -> AssistantOutputType:
        pass
