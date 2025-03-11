from typing import Generic

from math_rag.application.models.inference import LLMParams, LLMRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import (
    LLMParamsDocument,
    LLMRequestDocument,
)
from math_rag.shared.utils import TypeUtil


class LLMRequestMapping(
    BaseMapping[LLMRequest[LLMResponseType], LLMRequestDocument],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(target: LLMRequestDocument) -> LLMRequest[LLMResponseType]:
        # return LLMRequest(
        #     id=target.id,
        #     conversation: LLMConversation,
        #     params: LLMParams
        # )
        pass

    @staticmethod
    def to_target(source: LLMRequest[LLMResponseType]) -> LLMRequestDocument:
        return LLMRequestDocument(
            id=source.id,
            model=source.model,
            temperature=source.temperature,
            top_logprobs=source.top_logprobs,
            reasoning_effort=source.reasoning_effort,
            max_completion_tokens=source.max_completion_tokens,
            response_type=TypeUtil.to_fqn(source.response_type),
            metadata=source.metadata,
            n=source.n,
        )
