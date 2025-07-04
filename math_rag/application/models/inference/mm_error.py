from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.enums.inference import MMErrorRetryPolicy


class MMError(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    message: str
    code: str | None = None
    body: object | None = None
    retry_policy: MMErrorRetryPolicy
