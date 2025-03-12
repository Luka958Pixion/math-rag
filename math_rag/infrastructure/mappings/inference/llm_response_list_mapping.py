from openai.types.chat import ChatCompletion, ParsedChatCompletion

from math_rag.application.models.inference import LLMResponse, LLMResponseList
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping


class LLMResponseListMapping(
    BaseMapping[LLMResponseList[LLMResponseType], ChatCompletion | ParsedChatCompletion]
):
    @staticmethod
    def to_source(
        target: ChatCompletion | ParsedChatCompletion, **kwargs
    ) -> LLMResponseList[LLMResponseType]:
        return LLMResponseList(
            request_id=kwargs['request_id'],
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
