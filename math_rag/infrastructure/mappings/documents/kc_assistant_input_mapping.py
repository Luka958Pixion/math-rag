from math_rag.application.models.assistants import KCAssistantInput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import KCAssistantInputDocument


class KCAssistantInputMapping(BaseMapping[KCAssistantInput, KCAssistantInputDocument]):
    @classmethod
    def to_source(cls, target: KCAssistantInputDocument) -> KCAssistantInput:
        return cls(
            id=target._id,
            katex=target.katex,
            error=target.error,
        )

    @classmethod
    def to_target(cls, source: KCAssistantInput) -> KCAssistantInputDocument:
        return cls(
            _id=source.id,
            katex=source.katex,
            error=source.error,
        )
