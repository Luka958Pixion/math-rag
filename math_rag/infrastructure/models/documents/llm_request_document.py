from uuid import UUID

from pydantic import BaseModel

from .llm_conversation_document import LLMConversationDocument
from .llm_params_document import LLMParamsDocument


class LLMRequestDocument(BaseModel):
    _id: UUID
    _type: str
    conversation: LLMConversationDocument
    params: LLMParamsDocument
