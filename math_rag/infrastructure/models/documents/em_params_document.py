from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class EMParamsDocument(BaseDocument):
    id: UUID
    model: str
    dimensions: int | None = None

    inference_provider: str
    model_provider: str
