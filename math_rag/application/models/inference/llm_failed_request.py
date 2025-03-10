from typing import Generic

from pydantic import BaseModel

from math_rag.application.types.inference import LLMResponseType

from .llm_error import LLMError
from .llm_request import LLMRequest


class LLMFailedRequest(BaseModel, Generic[LLMResponseType]):
    request: LLMRequest[LLMResponseType]
    errors: list[LLMError]
