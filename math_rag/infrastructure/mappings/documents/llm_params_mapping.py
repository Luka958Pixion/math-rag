from math_rag.application.models.inference import LLMParams
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMParamsDocument


class LLMParamsMapping(BaseMapping[LLMParams, LLMParamsDocument]):
    @staticmethod
    def to_source(target: LLMParamsDocument) -> LLMParams:
        return LLMParams(
            id=target._id,
            model=target.model,
            temperature=target.temperature,
            top_logprobs=target.top_logprobs,
            reasoning_effort=target.reasoning_effort,
            max_completion_tokens=target.max_completion_tokens,
            response_type=target.response_type,
            metadata=target.metadata,
            n=target.n,
        )

    @staticmethod
    def to_target(source: LLMParams) -> LLMParamsDocument:
        return LLMParamsDocument(
            _id=source.id,
            _type=...,
            model=source.model,
            temperature=source.temperature,
            top_logprobs=source.top_logprobs,
            reasoning_effort=source.reasoning_effort,
            max_completion_tokens=source.max_completion_tokens,
            response_type=source.response_type,
            metadata=source.metadata,
            n=source.n,
        )
