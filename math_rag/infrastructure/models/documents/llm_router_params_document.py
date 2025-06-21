from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class LLMRouterParamsDocument(BaseDocument):
    id: UUID
    inference_provider: str
    model_provider: str
