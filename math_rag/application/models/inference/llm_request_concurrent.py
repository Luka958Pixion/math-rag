from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types.inference import LLMResponseType

from .llm_request import LLMRequest


class LLMRequestConcurrent(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    requests: list[LLMRequest[LLMResponseType]]
