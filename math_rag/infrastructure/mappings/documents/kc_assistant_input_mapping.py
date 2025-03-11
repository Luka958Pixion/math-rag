from math_rag.application.models.assistants import KCAssistantInput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import KCAssistantInputDocument


class KCAssistantInputMapping(BaseMapping[KCAssistantInput, KCAssistantInputDocument]):
    @staticmethod
    def to_source(target: KCAssistantInputDocument) -> KCAssistantInput:
        return KCAssistantInput(
            id=target.id,
            katex=target.katex,
            error=target.error,
        )

    @staticmethod
    def to_target(source: KCAssistantInput) -> KCAssistantInputDocument:
        return KCAssistantInputDocument(
            id=source.id,
            katex=source.katex,
            error=source.error,
        )
