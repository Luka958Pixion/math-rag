from typing import Generic
from uuid import UUID

from pydantic import BaseModel

from math_rag.application.types.inference import LLMResponseType


class LLMParamsDocument(BaseModel, Generic[LLMResponseType]):
    _id: UUID
    model: str
    temperature: float
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: type[LLMResponseType]
    metadata: dict[str, str]
    n: int = 1
