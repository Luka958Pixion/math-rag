from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class KCAssistantInputDocument(BaseDocument):
    id: UUID
    katex: str
    error: str
