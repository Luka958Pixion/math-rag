from typing import Generic

from pydantic import BaseModel

from math_rag.application.types import LLMResponseType

from .llm_conversation import LLMConversation
from .llm_params import LLMParams


class LLMRequest(BaseModel, Generic[LLMResponseType]):
    conversation: LLMConversation
    params: LLMParams[LLMResponseType]
