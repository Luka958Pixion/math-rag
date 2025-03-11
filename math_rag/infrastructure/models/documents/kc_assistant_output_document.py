from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class KCAssistantOutputDocument(BaseDocument):
    id: UUID
    katex: str
