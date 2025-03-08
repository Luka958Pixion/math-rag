from abc import ABC, abstractmethod
from typing import Generic, Type

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import (
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class BaseAssistant(ABC, Generic[AssistantInputType, AssistantOutputType]):
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

    @abstractmethod
    async def assist(self, input: AssistantInputType) -> AssistantOutputType:
        pass

    @abstractmethod
    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: Type[AssistantOutputType],
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
        response_type: Type[AssistantOutputType],
    ) -> list[AssistantOutputType] | None:
        pass
