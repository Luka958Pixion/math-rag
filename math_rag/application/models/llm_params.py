from typing import Generic

from pydantic import BaseModel, model_validator

from math_rag.application.types import LLMResponseType


class LLMParams(BaseModel, Generic[LLMResponseType]):
    model: str
    temperature: float
    logprobs: bool | None = None
    top_logprobs: int | None = None
    response_type: LLMResponseType

    @model_validator(mode='after')
    def check_dependencies(self):
        if self.logprobs and self.top_logprobs is None:
            raise ValueError('When logprobs is True, top_logprobs must not be None')

        return self
