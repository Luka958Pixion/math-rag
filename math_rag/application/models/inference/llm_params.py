from typing import Generic, Type

from pydantic import BaseModel, field_validator

from math_rag.application.types.inference import LLMResponseType


class LLMParams(BaseModel, Generic[LLMResponseType]):
    model: str
    temperature: float
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    response_type: Type[LLMResponseType]
    n: int = 1

    @field_validator('response_type', mode='before')
    def allow_python_types(cls, value):
        return value
