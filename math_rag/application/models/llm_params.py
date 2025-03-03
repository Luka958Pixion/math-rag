from pydantic import BaseModel, model_validator

from math_rag.application.enums import LLMResponseFormat


class LLMParams(BaseModel):
    model: str
    response_format: LLMResponseFormat
    temperature: float
    logprobs: bool | None = None
    top_logprobs: int | None = None
    json_schema: dict | None = None

    @model_validator(mode='after')
    def check_dependencies(self):
        if self.logprobs and self.top_logprobs is None:
            raise ValueError('When logprobs is True, top_logprobs must not be None')

        if (
            self.response_format == LLMResponseFormat.JSON_SCHEMA
            and self.json_schema is None
        ):
            raise ValueError(
                'When response_format is JSON_SCHEMA, json_schema must not be None'
            )

        return self
