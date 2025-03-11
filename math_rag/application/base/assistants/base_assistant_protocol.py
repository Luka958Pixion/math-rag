from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import (
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class BaseAssistantProtocol(ABC, Generic[AssistantInputType, AssistantOutputType]):
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    @abstractmethod
    def to_request(self, input: AssistantInputType) -> LLMRequest[AssistantOutputType]:
        pass

    @abstractmethod
    def from_response_list(
        self, response_list: LLMResponseList[AssistantOutputType]
    ) -> AssistantOutputType:
        pass
