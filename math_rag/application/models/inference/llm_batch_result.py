from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types.inference import LLMResponseType

from .llm_failed_request import LLMFailedRequest
from .llm_response_list import LLMResponseList


class LLMBatchResult(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    response_lists: list[LLMResponseList[LLMResponseType]]
    failed_requests: list[LLMFailedRequest[LLMResponseType]]
