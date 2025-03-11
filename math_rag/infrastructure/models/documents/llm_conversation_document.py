from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .llm_message_document import LLMMessageDocument


class LLMConversationDocument(BaseDocument):
    id: UUID
    messages: list[LLMMessageDocument]
