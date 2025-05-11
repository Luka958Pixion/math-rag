from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class KatexCorrectorAssistantInputDocument(BaseDocument):
    id: UUID
    katex: str
    error: str
