from datetime import datetime
from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types.inference import LLMResponseType

from .llm_batch_request import LLMBatchRequest


class LLMBatchRequestScheduleEntry(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    batch_request: LLMBatchRequest[LLMResponseType]
    timestamp: datetime
