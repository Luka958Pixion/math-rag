from typing import Generic

from huggingface_hub.inference._generated.types import ChatCompletionOutputComplete

from math_rag.application.models.inference import LLMResponse, LLMTextResponse
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping


class LLMResponseMapping(
    BaseMapping[
        LLMResponse[LLMResponseType],
        ChatCompletionOutputComplete,
    ],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(
        target: ChatCompletionOutputComplete, **kwargs
    ) -> LLMResponse[LLMResponseType]:
        response_type: type[LLMResponseType] = kwargs['response_type']

        return LLMResponse(
            content=response_type.model_validate_json(target.message.content)
            if response_type is not LLMTextResponse
            else target.message.content
        )

    @staticmethod
    def to_target(
        source: LLMResponse[LLMResponseType],
    ) -> ChatCompletionOutputComplete:
        raise NotImplementedError()
