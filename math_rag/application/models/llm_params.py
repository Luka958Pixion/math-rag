from typing import Generic, Type

from pydantic import BaseModel, field_validator, model_validator

from math_rag.application.types import LLMResponseType


class LLMParams(BaseModel, Generic[LLMResponseType]):
    model: str
    temperature: float
    logprobs: bool | None = None
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    response_type: Type[LLMResponseType]
    n: int = 1

    @field_validator('response_type', mode='before')
    def allow_python_types(cls, value):
        return value

    @model_validator(mode='after')
    def check_dependencies(self):
        if self.logprobs and self.top_logprobs is None:
            raise ValueError('When logprobs is True, top_logprobs must not be None')

        return self
