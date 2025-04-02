from typing import Any, Generic
from uuid import UUID

from math_rag.application.models.inference import (
    LLMParams,
    LLMRequest,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping

from .llm_conversation_mapping import LLMConversationMapping


class LLMRequestMapping(
    BaseMapping[LLMRequest[LLMResponseType], dict[str, Any]], Generic[LLMResponseType]
):
    @staticmethod
    def to_source(target: dict[str, Any], **kwargs) -> LLMRequest[LLMResponseType]:
        request_id = kwargs['request_id']
        input_id = UUID(target['metadata']['input_id'])
        response_type = kwargs['response_type'].bind(input_id)

        return LLMRequest(
            id=request_id,
            conversation=LLMConversationMapping.to_source(target['messages']),
            params=LLMParams[LLMResponseType](
                model=target['model'],
                temperature=target['temperature'],
                logprobs=target['logprobs'],
                top_logprobs=target['top_logprobs'],
                response_type=response_type,
                max_completion_tokens=target['max_tokens'],
                n=target.get('n', 1),
            ),
        )

    @staticmethod
    def to_target(source: LLMRequest[LLMResponseType]) -> dict[str, Any]:
        response_format = (
            None
            if source.params.response_type is LLMTextResponse
            else source.params.response_type.model_json_schema()
        )

        return {
            'messages': LLMConversationMapping.to_target(source.conversation),
            'model': source.params.model,
            'temperature': source.params.temperature,
            'logprobs': source.params.top_logprobs is not None,
            'top_logprobs': source.params.top_logprobs,
            'response_format': response_format,
            'max_tokens': source.params.max_completion_tokens,
            'n': source.params.n,
        }
