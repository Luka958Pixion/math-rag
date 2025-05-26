from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.enums.inference import LLMErrorRetryPolicy
from math_rag.application.types.inference import LLMResponseType

from .llm_error import LLMError
from .llm_request import LLMRequest


class LLMFailedRequest(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    request: LLMRequest[LLMResponseType]
    errors: list[LLMError]

    def is_retry_allowed(self) -> bool:
        return all(
            error.retry_policy == LLMErrorRetryPolicy.RETRY for error in self.errors
        )
