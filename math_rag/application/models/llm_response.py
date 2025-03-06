from typing import Generic

from pydantic import BaseModel

from math_rag.application.types import LLMResponseType


class LLMResponse(BaseModel, Generic[LLMResponseType]):
    content: LLMResponseType
