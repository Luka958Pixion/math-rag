from uuid import UUID

from pydantic import BaseModel


class LLMParamsDocument(BaseModel):
    _id: UUID
    _type: str
    model: str
    temperature: float
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: type
    metadata: dict[str, str]
    n: int = 1
