from typing import Generic

from pydantic import BaseModel, Field

from math_rag.application.types.inference import LLMResponseType

from .llm_error import LLMError
from .llm_request import LLMRequest


class LLMRequestTracker(BaseModel, Generic[LLMResponseType]):
    request: LLMRequest[LLMResponseType]
    errors: list[LLMError] = Field(default_factory=list)
    token_consumption: int
    attempts_left: int
