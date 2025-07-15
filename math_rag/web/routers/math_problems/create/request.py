from uuid import UUID

from pydantic import BaseModel, model_validator


class Request(BaseModel):
    math_expression_index_id: UUID
    token: str | None = None
    url: str | None = None

    @model_validator(mode='after')
    def check_token_xor_url(cls, model: 'Request') -> 'Request':
        if model.token is not None and model.url is not None:
            raise ValueError('Either token or url must be set')

        return model
