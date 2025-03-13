from typing import Generic

from openai import NOT_GIVEN
from openai.lib._parsing._completions import (
    parse_chat_completion,
)
from openai.types.chat import ChatCompletion

from math_rag.application.models.inference import (
    LLMResponse,
    LLMResponseList,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping


class LLMResponseListMapping(
    BaseMapping[LLMResponseList[LLMResponseType], ChatCompletion],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(target: ChatCompletion, **kwargs) -> LLMResponseList[LLMResponseType]:
        request_id = kwargs['request_id']
        response_type = kwargs.get('response_type')
        print(response_type, type(response_type))

        if response_type and response_type is not LLMTextResponse:
            target = parse_chat_completion(
                response_format=response_type,
                input_tools=NOT_GIVEN,
                chat_completion=target,
            )

        return LLMResponseList(
            request_id=request_id,
            responses=[
                LLMResponse[LLMResponseType](
                    content=choice.message.content
                    if isinstance(choice, ChatCompletion)
                    else choice.message.parsed
                )
                for choice in target.choices
            ],
        )

    @staticmethod
    def to_target(source: LLMResponseList) -> ChatCompletion:
        raise NotImplementedError()
