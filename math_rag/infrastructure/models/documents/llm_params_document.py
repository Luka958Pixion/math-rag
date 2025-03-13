from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class LLMParamsDocument(BaseDocument):
    id: UUID
    model: str
    temperature: float
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: str
    metadata: dict[str, str] | None = None
    store: bool | None = None
    n: int = 1
