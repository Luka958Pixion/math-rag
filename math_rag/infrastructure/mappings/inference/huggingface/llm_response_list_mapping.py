from typing import Generic

from huggingface_hub.inference._generated.types import ChatCompletionOutput

from math_rag.application.models.inference import LLMResponseList
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping

from .llm_response_mapping import LLMResponseMapping


class LLMResponseListMapping(
    BaseMapping[LLMResponseList[LLMResponseType], ChatCompletionOutput],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(
        target: ChatCompletionOutput, **kwargs
    ) -> LLMResponseList[LLMResponseType]:
        request_id = kwargs['request_id']
        input_id = kwargs.get('input_id')
        response_type = kwargs['response_type']

        if input_id:
            response_type = response_type.bind(input_id)

        return LLMResponseList(
            request_id=request_id,
            responses=[
                LLMResponseMapping[LLMResponseType].to_source(
                    choice.message, response_type=response_type
                )
                for choice in target.choices
            ],
        )

    @staticmethod
    def to_target(source: LLMResponseList[LLMResponseType]) -> ChatCompletionOutput:
        raise NotImplementedError()
