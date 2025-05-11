from abc import ABC, abstractmethod
from typing import Generic

from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class BaseBasicAssistant(ABC, Generic[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    async def assist(self, input: AssistantInputType) -> AssistantOutputType | None:
        pass
