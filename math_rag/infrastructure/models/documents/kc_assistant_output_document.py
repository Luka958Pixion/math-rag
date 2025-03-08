from uuid import UUID

from pydantic import BaseModel

from math_rag.application.models.assistants import KCAssistantOutput


class KCAssistantOutputDocument(BaseModel):
    _id: UUID
    katex: str

    @classmethod
    def from_internal(cls, inter: KCAssistantOutput) -> 'KCAssistantOutputDocument':
        return cls(
            _id=inter.id,
            katex=inter.katex,
        )

    @classmethod
    def to_internal(cls, doc: 'KCAssistantOutputDocument') -> KCAssistantOutput:
        return cls(
            id=doc._id,
            katex=doc.katex,
        )
