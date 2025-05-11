from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class KatexCorrectorAssistantOutputDocument(BaseDocument):
    id: UUID
    katex: str
