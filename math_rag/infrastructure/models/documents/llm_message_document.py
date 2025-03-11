from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class LLMMessageDocument(BaseDocument):
    id: UUID
    role: str
    content: str
