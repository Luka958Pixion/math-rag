from math_rag.application.models.inference import LLMMessage
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMMessageDocument


class LLMMessageMapping(BaseMapping[LLMMessage, LLMMessageDocument]):
    @staticmethod
    def to_source(target: LLMMessageDocument) -> LLMMessage:
        return LLMMessage(id=target.id, role=target.role, content=target.content)

    @staticmethod
    def to_target(source: LLMMessage) -> LLMMessageDocument:
        return LLMMessageDocument(id=source.id, role=source.role, content=source.content)
