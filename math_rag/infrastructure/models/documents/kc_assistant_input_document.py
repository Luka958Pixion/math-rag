from uuid import UUID

from pydantic import BaseModel

from math_rag.application.models.assistants import KCAssistantInput


class KCAssistantInputDocument(BaseModel):
    _id: UUID
    katex: str
    error: str

    @classmethod
    def from_internal(cls, inter: KCAssistantInput) -> 'KCAssistantInputDocument':
        return cls(
            _id=inter.id,
            katex=inter.katex,
            error=inter.error,
        )

    @classmethod
    def to_internal(cls, doc: 'KCAssistantInputDocument') -> KCAssistantInput:
        return cls(
            id=doc._id,
            katex=doc.katex,
            error=doc.error,
        )
