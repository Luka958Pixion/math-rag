from typing import Any

from math_rag.application.models.inference import LLMRequest, LLMTextResponse
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping


class LLMRequestMapping(BaseMapping[LLMRequest[LLMResponseType], dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any]) -> LLMRequest[LLMResponseType]:
        raise NotImplementedError()

    @staticmethod
    def to_target(source: LLMRequest[LLMResponseType]) -> dict[str, Any]:
        return {
            'model': source.params.model,
            'messages': [
                {'role': message.role, 'content': message.content}
                for message in source.conversation.messages
            ],
            'response_format': {'type': 'text'}
            if source.params.response_type is LLMTextResponse
            else source.params.response_type,
            'temperature': source.params.temperature,
            'logprobs': source.params.top_logprobs is not None,
            'top_logprobs': source.params.top_logprobs,
            'max_completion_tokens': source.params.max_completion_tokens,
            'metadata': source.params.metadata,
        }
