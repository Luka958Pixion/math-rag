from uuid import UUID

from pydantic import BaseModel

from .llm_message_document import LLMMessageDocument


class LLMConversationDocument(BaseModel):
    _id: UUID
    messages: list[LLMMessageDocument]
