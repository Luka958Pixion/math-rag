from uuid import UUID

from math_rag.application.enums.inference import MMErrorRetryPolicy
from math_rag.infrastructure.base import BaseDocument


class MMErrorDocument(BaseDocument):
    id: UUID
    message: str
    code: str | None
    body: object | None
    retry_policy: MMErrorRetryPolicy
