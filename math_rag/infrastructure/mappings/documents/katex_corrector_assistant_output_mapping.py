from math_rag.application.models.assistants import KatexCorrectorAssistantOutput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import (
    KatexCorrectorAssistantOutputDocument,
)


class KatexCorrectorAssistantOutputMapping(
    BaseMapping[KatexCorrectorAssistantOutput, KatexCorrectorAssistantOutputDocument]
):
    @staticmethod
    def to_source(
        target: KatexCorrectorAssistantOutputDocument,
    ) -> KatexCorrectorAssistantOutput:
        return KatexCorrectorAssistantOutput(
            id=target.id,
            katex=target.katex,
        )

    @staticmethod
    def to_target(
        source: KatexCorrectorAssistantOutput,
    ) -> KatexCorrectorAssistantOutputDocument:
        return KatexCorrectorAssistantOutputDocument(
            id=source.id,
            katex=source.katex,
        )
