from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.models.inference import LLMRequestBatch
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class BaseBatchAssistantProtocol(ABC, Generic[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    def encode_to_request_batch(
        self, inputs: list[AssistantInputType]
    ) -> LLMRequestBatch[AssistantOutputType]:
        pass
