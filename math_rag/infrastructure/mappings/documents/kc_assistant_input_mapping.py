from math_rag.application.models.assistants import KCAssistantInput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import KCAssistantInputDocument


class KCAssistantInputMapping(BaseMapping[KCAssistantInput, KCAssistantInputDocument]):
    @staticmethod
    def to_source(target: KCAssistantInputDocument) -> KCAssistantInput:
        kc_assistant_input = KCAssistantInput(
            id=target._id,
            katex=target.katex,
            error=target.error,
        )

        return kc_assistant_input

    @staticmethod
    def to_target(source: KCAssistantInput) -> KCAssistantInputDocument:
        kc_assistant_input_document = KCAssistantInputDocument(
            _id=source.id,
            katex=source.katex,
            error=source.error,
        )

        return kc_assistant_input_document
