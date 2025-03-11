from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class LLMErrorDocument(BaseDocument):
    id: UUID
    message: str
    body: object | None
