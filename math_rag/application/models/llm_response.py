from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types import LLMResponseType

from .llm_logprob import LLMLogprob


class LLMResponse(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4, exclude=True)
    content: LLMResponseType
    logprobs: list[LLMLogprob] | None = None
