from uuid import UUID

from math_rag.application.enums.inference import EMErrorRetryPolicy
from math_rag.infrastructure.base import BaseDocument


class EMErrorDocument(BaseDocument):
    id: UUID
    message: str
    code: str | None
    body: object | None
    retry_policy: EMErrorRetryPolicy
