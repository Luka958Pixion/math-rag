from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MMParamsDocument(BaseDocument):
    id: UUID
    model: str
