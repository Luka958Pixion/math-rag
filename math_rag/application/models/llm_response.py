from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar('T')


class LLMResponse(BaseModel, Generic[T]):
    value: T
    logprobs: dict[str, float] | None = None
