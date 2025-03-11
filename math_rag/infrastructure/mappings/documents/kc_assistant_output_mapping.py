from math_rag.application.models.assistants import KCAssistantOutput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import KCAssistantOutputDocument


class KCAssistantOutputMapping(
    BaseMapping[KCAssistantOutput, KCAssistantOutputDocument]
):
    @staticmethod
    def to_source(target: KCAssistantOutputDocument) -> KCAssistantOutput:
        return KCAssistantOutput(
            id=target._id,
            katex=target.katex,
        )

    @staticmethod
    def to_target(source: KCAssistantOutput) -> KCAssistantOutputDocument:
        return KCAssistantOutputDocument(
            _id=source.id,
            katex=source.katex,
        )
