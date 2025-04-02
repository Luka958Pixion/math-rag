from typing import Generic

from math_rag.application.models.inference import LLMResponse
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from openai.types.chat import ChatCompletionMessage, ParsedChatCompletionMessage


class LLMResponseMapping(
    BaseMapping[
        LLMResponse[LLMResponseType],
        ChatCompletionMessage | ParsedChatCompletionMessage,
    ],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(
        target: ChatCompletionMessage | ParsedChatCompletionMessage,
    ) -> LLMResponse[LLMResponseType]:
        return LLMResponse(
            content=target.parsed
            if isinstance(target, ParsedChatCompletionMessage)
            else target.content,
        )

    @staticmethod
    def to_target(
        source: LLMResponse[LLMResponseType],
    ) -> ChatCompletionMessage | ParsedChatCompletionMessage:
        raise NotImplementedError()
