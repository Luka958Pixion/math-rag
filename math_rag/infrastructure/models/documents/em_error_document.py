from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class EMErrorDocument(BaseDocument):
    id: UUID
    message: str
    body: object | None
