from typing import Generic

from pydantic import BaseModel, field_validator

from math_rag.application.types.inference import LLMResponseType


class LLMParams(BaseModel, Generic[LLMResponseType]):
    model: str
    temperature: float
    top_logprobs: int | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    response_type: type[LLMResponseType]
    metadata: dict[str, str]
    n: int = 1

    @field_validator('response_type', mode='before')
    @classmethod
    def allow_python_types(cls, value: type[LLMResponseType]):
        return value

    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, value: dict[str, str]):
        if len(value) > 16:
            raise ValueError('Metadata cannot have more than 16 key-value pairs')

        for key, value in value.items():
            if len(key) > 64:
                raise ValueError(f'Metadata key {key} exceeds 64 characters')

            if len(value) > 512:
                raise ValueError(f'Metadata value for key {key} exceeds 512 characters')

        return value
