from typing import Generic

from pydantic import BaseModel

from math_rag.application.types import LLMResponseType

from .llm_request import LLMRequest


class LLMRequestBatch(BaseModel, Generic[LLMResponseType]):
    requests: list[LLMRequest[LLMResponseType]]
