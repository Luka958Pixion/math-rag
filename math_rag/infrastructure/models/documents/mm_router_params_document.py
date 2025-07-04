from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MMRouterParamsDocument(BaseDocument):
    id: UUID
    inference_provider: str
    model_provider: str
