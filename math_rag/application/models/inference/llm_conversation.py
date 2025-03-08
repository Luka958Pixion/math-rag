from pydantic import BaseModel

from .llm_message import LLMMessage


class LLMConversation(BaseModel):
    messages: list[LLMMessage]
