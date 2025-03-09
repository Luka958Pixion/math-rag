from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from math_rag.application.types.inference import LLMResponseType

from .llm_logprob import LLMLogprob


class LLMResponse(BaseModel, Generic[LLMResponseType]):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
    content: LLMResponseType
    logprobs: list[LLMLogprob] | None = None
