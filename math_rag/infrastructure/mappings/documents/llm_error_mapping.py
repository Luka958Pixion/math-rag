from math_rag.application.models.inference import LLMError
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMErrorDocument


class LLMErrorMapping(BaseMapping[LLMError, LLMErrorDocument]):
    @staticmethod
    def to_source(target: LLMErrorDocument) -> LLMError:
        return LLMError(
            id=target.id,
            code=target.code,
            message=target.message,
            body=target.body,
            retry_policy=target.retry_policy,
        )

    @staticmethod
    def to_target(source: LLMError) -> LLMErrorDocument:
        return LLMErrorDocument(
            id=source.id,
            code=source.code,
            message=source.message,
            body=source.body,
            retry_policy=source.retry_policy,
        )
