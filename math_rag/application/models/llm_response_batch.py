from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types import LLMResponseType

from .llm_request_batch import LLMRequestBatch
from .llm_response import LLMResponse


class LLMResponseBatch(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    incomplete_request_batch: LLMRequestBatch[LLMResponseType]
    nested_responses: list[LLMResponse[LLMResponseType]]
