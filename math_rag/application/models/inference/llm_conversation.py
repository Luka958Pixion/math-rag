from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .llm_message import LLMMessage


class LLMConversation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    messages: list[LLMMessage]
