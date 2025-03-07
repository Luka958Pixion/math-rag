from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types import LLMResponseType

from .llm_conversation import LLMConversation
from .llm_params import LLMParams


class LLMRequest(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    conversation: LLMConversation
    params: LLMParams[LLMResponseType]
