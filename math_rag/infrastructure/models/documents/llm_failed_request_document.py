from typing import Generic
from uuid import UUID

from pydantic import BaseModel

from .llm_error_document import LLMErrorDocument
from .llm_request_document import LLMRequestDocument


class LLMFailedRequestDocument(BaseModel):
    _id: UUID
    _type: str
    request: LLMRequestDocument
    errors: list[LLMErrorDocument]
