from math_rag.application.models.assistants import KCAssistantOutput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import KCAssistantOutputDocument


class KCAssistantOutputMapping(
    BaseMapping[KCAssistantOutput, KCAssistantOutputDocument]
):
    @classmethod
    def to_source(cls, target: KCAssistantOutputDocument) -> KCAssistantOutput:
        return cls(
            id=target._id,
            katex=target.katex,
        )

    @classmethod
    def to_target(cls, source: KCAssistantOutput) -> KCAssistantOutputDocument:
        return cls(
            _id=source.id,
            katex=source.katex,
        )
