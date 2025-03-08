from abc import abstractmethod

from math_rag.application.models.inference import LLMRequestBatch
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)

from .base_assistant import BaseAssistant


class BaseBatchAssistant(BaseAssistant[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    def to_request_batch(
        self, inputs: list[AssistantInputType]
    ) -> LLMRequestBatch[AssistantOutputType]:
        pass

    @abstractmethod
    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: type[AssistantOutputType],
        delay: float,
        num_retries: int,
    ) -> tuple[list[AssistantInputType], list[AssistantOutputType]]:
        pass

    @abstractmethod
    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        pass

    @abstractmethod
    async def batch_assist_result(
        self,
        batch_id: str,
        response_type: type[AssistantOutputType],
    ) -> list[AssistantOutputType] | None:
        pass
