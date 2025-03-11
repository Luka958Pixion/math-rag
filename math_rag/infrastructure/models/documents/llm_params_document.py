from uuid import UUID

from pydantic import BaseModel, Field


class LLMParamsDocument(BaseModel):
    id: UUID = Field(serialization_alias='id')
    model: str
    temperature: float
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: str
    metadata: dict[str, str] | None = None
    n: int = 1
