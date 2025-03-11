from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .llm_conversation_document import LLMConversationDocument
from .llm_params_document import LLMParamsDocument


class LLMRequestDocument(BaseDocument):
    id: UUID
    _type: str
    conversation: LLMConversationDocument
    params: LLMParamsDocument
