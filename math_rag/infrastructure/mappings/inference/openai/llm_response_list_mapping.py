from typing import Generic

from math_rag.application.models.inference import (
    LLMResponseList,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from openai import NOT_GIVEN
from openai.lib._parsing._completions import (
    parse_chat_completion,
)
from openai.types.chat import ChatCompletion

from .llm_response_mapping import LLMResponseMapping


class LLMResponseListMapping(
    BaseMapping[LLMResponseList[LLMResponseType], ChatCompletion],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(target: ChatCompletion, **kwargs) -> LLMResponseList[LLMResponseType]:
        request_id = kwargs['request_id']
        input_id = kwargs.get('input_id')
        response_type = kwargs['response_type']

        if input_id:
            response_type = response_type.bind(input_id)

        if response_type is not LLMTextResponse:
            target = parse_chat_completion(
                response_format=response_type,
                input_tools=NOT_GIVEN,
                chat_completion=target,
            )

        return LLMResponseList(
            request_id=request_id,
            responses=[
                LLMResponseMapping[LLMResponseType].to_source(choice.message)
                for choice in target.choices
            ],
        )

    @staticmethod
    def to_target(source: LLMResponseList[LLMResponseType]) -> ChatCompletion:
        raise NotImplementedError()
