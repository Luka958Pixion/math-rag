from abc import abstractmethod
from uuid import UUID

from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)

from .base_basic_assistant import BaseBasicAssistant


class BaseBatchAssistant(BaseBasicAssistant[AssistantInputType, AssistantOutputType]):
    @abstractmethod
    async def batch_assist(
        self, inputs: list[AssistantInputType], *, use_scheduler: bool
    ) -> list[AssistantOutputType]:
        pass

    @abstractmethod
    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        pass

    @abstractmethod
    async def batch_assist_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
    ) -> list[AssistantOutputType] | None:
        pass
