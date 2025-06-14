from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class LLMParamsDocument(BaseDocument):
    id: UUID
    model: str
    temperature: float
    logprobs: bool | None = None
    top_logprobs: int | None = None
    top_p: float | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: str
    metadata: dict[str, str] | None = None
    store: bool | None = None
    n: int = 1

    inference_provider: str
    model_provider: str
