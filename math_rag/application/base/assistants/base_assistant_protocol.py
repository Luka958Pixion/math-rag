from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.models.inference import LLMRequest, LLMResponseList
from math_rag.application.types.assistants import AssistantInputType, AssistantOutputType


class BaseAssistantProtocol(ABC, Generic[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    def encode_to_request(self, input: AssistantInputType) -> LLMRequest[AssistantOutputType]:
        pass

    @abstractmethod
    def decode_from_response_list(
        self, response_list: LLMResponseList[AssistantOutputType]
    ) -> AssistantOutputType:
        pass
