from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from math_rag.application.types.inference import LLMResponseType

from .llm_request import LLMRequest


class LLMBatchRequest(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    requests: list[LLMRequest[LLMResponseType]]

    @model_validator(mode='after')
    def check_models_match(self) -> 'LLMBatchRequest':
        if not self.requests:
            return self

        first_model = self.requests[0].params.model

        for i, request in enumerate(self.requests[1:], start=1):
            if request.params.model != first_model:
                raise ValueError(
                    f'All requests must use the same model. '
                    f'Request at index 0 uses model: {first_model}, '
                    f'but request at index {i} uses model: {request.params.model}'
                )

        return self
