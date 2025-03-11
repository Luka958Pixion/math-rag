from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .llm_error_document import LLMErrorDocument
from .llm_request_document import LLMRequestDocument


class LLMFailedRequestDocument(BaseDocument):
    id: UUID
    _type: str
    request: LLMRequestDocument
    errors: list[LLMErrorDocument]
