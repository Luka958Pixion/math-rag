from typing import Generic

from math_rag.application.models.inference import LLMParams
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMParamsDocument
from math_rag.shared.utils import TypeUtil


class LLMParamsMapping(
    BaseMapping[LLMParams[LLMResponseType], LLMParamsDocument], Generic[LLMResponseType]
):
    @staticmethod
    def to_source(target: LLMParamsDocument) -> LLMParams[LLMResponseType]:
        return LLMParams[LLMResponseType](
            id=target.id,
            model=target.model,
            temperature=target.temperature,
            logprobs=target.logprobs,
            top_logprobs=target.top_logprobs,
            top_p=target.top_p,
            reasoning_effort=target.reasoning_effort,
            max_completion_tokens=target.max_completion_tokens,
            response_type=TypeUtil[LLMResponseType].from_fqn(target.response_type),
            metadata=target.metadata,
            store=target.store,
            n=target.n,
        )

    @staticmethod
    def to_target(source: LLMParams[LLMResponseType]) -> LLMParamsDocument:
        return LLMParamsDocument(
            id=source.id,
            model=source.model,
            temperature=source.temperature,
            logprobs=source.logprobs,
            top_logprobs=source.top_logprobs,
            top_p=source.top_p,
            reasoning_effort=source.reasoning_effort,
            max_completion_tokens=source.max_completion_tokens,
            response_type=TypeUtil.to_fqn(source.response_type),
            metadata=source.metadata,
            store=source.store,
            n=source.n,
        )
