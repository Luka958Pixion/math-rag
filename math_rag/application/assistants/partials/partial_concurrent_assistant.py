from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseConcurrentAssistant,
)
from math_rag.application.base.inference import BaseLLM
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)


class PartialConcurrentAssistant(
    BaseConcurrentAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)

    async def concurrent_generate(
        self,
        inputs: list[AssistantInputType],
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_attempts: int,
    ) -> tuple[list[AssistantInputType], list[AssistantOutputType]]:
        # TODO
        pass
