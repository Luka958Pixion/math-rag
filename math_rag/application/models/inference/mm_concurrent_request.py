from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from .mm_request import MMRequest


class MMConcurrentRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    requests: list[MMRequest]

    @model_validator(mode='after')
    def check_models_match(self) -> 'MMConcurrentRequest':
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
