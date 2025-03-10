from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types.inference import LLMResponseType

from .llm_request_batch import LLMRequestBatch
from .llm_response_list import LLMResponseList


class LLMResponseBatchPlus(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    incomplete_request_batch: LLMRequestBatch[LLMResponseType]
    response_lists: list[LLMResponseList[LLMResponseType]]
