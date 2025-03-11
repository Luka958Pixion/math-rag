from abc import abstractmethod

from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)

from .base_assistant import BaseAssistant


class BaseConcurrentAssistant(BaseAssistant[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    async def concurrent_generate(
        self,
        inputs: list[AssistantInputType],
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_attempts: int,
    ) -> tuple[list[AssistantInputType], list[AssistantOutputType]]:
        pass
