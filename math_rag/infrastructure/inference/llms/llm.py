from enum import Enum

from openai import NOT_GIVEN, AsyncOpenAI
from openai.types import (
    ResponseFormatJSONObject,
    ResponseFormatJSONSchema,
    ResponseFormatText,
)


class ResponseFormat(str, Enum):
    TEXT = 'text'
    JSON_OBJECT = 'json_object'
    JSON_SCHEMA = 'json_schema'


class LLM:
    def __init__(self, model: str, base_url: str = None, api_key: str = None):
        self.model = model
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    async def generate(self, prompt: str) -> str:
        # NOTE for json schema:
        response_format = ResponseFormatJSONSchema(
            json_schema={
                'name': ...,
                'description': ...,  # optional
                'schema': ...,  # optional
                'strict': ...,  # optional
            }
        )

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            response_format=response_format,
            logprobs=True,
            temperature=0.0,
            top_logprobs=5,
        )

        return completion.choices[0].message.content
