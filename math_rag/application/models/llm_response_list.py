from typing import Generic

from pydantic import BaseModel

from math_rag.application.types import LLMResponseType

from .llm_response import LLMResponse


class LLMResponseList(BaseModel, Generic[LLMResponseType]):
    responses: list[LLMResponse[LLMResponseType]]
