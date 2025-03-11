from math_rag.application.models.inference import LLMError
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMErrorDocument


class LLMErrorMapping(BaseMapping[LLMError, LLMErrorDocument]):
    @staticmethod
    def to_source(target: LLMErrorDocument) -> LLMError:
        return LLMError(id=target.id, message=target.message, body=target.body)

    @staticmethod
    def to_target(source: LLMError) -> LLMErrorDocument:
        return LLMErrorDocument(id=source.id, message=source.message, body=source.body)
