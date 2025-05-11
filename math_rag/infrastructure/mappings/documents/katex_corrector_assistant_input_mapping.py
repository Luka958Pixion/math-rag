from math_rag.application.models.assistants import KatexCorrectorAssistantInput
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import (
    KatexCorrectorAssistantInputDocument,
)


class KatexCorrectorAssistantInputMapping(
    BaseMapping[KatexCorrectorAssistantInput, KatexCorrectorAssistantInputDocument]
):
    @staticmethod
    def to_source(
        target: KatexCorrectorAssistantInputDocument,
    ) -> KatexCorrectorAssistantInput:
        return KatexCorrectorAssistantInput(
            id=target.id,
            katex=target.katex,
            error=target.error,
        )

    @staticmethod
    def to_target(
        source: KatexCorrectorAssistantInput,
    ) -> KatexCorrectorAssistantInputDocument:
        return KatexCorrectorAssistantInputDocument(
            id=source.id,
            katex=source.katex,
            error=source.error,
        )
