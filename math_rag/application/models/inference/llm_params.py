from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from math_rag.application.types.inference import LLMResponseType


class LLMParams(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    model: str
    temperature: float
    logprobs: bool | None = None
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: type[LLMResponseType]
    metadata: dict[str, str] | None = None
    store: bool | None = None
    n: int = 1

    @field_validator('response_type', mode='before')
    def allow_python_types(cls, value: type[LLMResponseType]):
        return value

    @field_validator('metadata', mode='before')
    def validate_metadata(cls, value: dict[str, str] | None):
        if value is None:
            return

        if len(value) > 16:
            raise ValueError('Metadata cannot have more than 16 key-value pairs')

        for key, _value in value.items():
            if len(key) > 64:
                raise ValueError(f'Metadata key {key} exceeds 64 characters')

            if len(_value) > 512:
                raise ValueError(f'Metadata value for key {key} exceeds 512 characters')

        return value
