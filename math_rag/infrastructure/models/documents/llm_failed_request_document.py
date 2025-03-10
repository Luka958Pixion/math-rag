from typing import Generic
from uuid import UUID

from pydantic import BaseModel

from math_rag.application.models.inference import LLMError, LLMRequest
from math_rag.application.types.inference import LLMResponseType


class LLMFailedRequestDocument(BaseModel, Generic[LLMResponseType]):
    _id: UUID
    _type: str
    request: LLMRequest[LLMResponseType]
    errors: list[LLMError]
