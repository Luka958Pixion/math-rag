from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class BaseConcurrentAssistant(ABC, Generic[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    async def concurrent_assist(
        self,
        inputs: list[AssistantInputType],
    ) -> list[AssistantOutputType]:
        pass
