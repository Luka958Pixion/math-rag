from pydantic import BaseModel

from .llm_request import LLMRequest


class LLMRequestBatch(BaseModel):
    requests: list[LLMRequest]
