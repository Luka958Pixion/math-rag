from openai import AsyncOpenAI
from openai.types import (
    ResponseFormatJSONObject,
    ResponseFormatJSONSchema,
    ResponseFormatText,
)

from math_rag.application.base.inference import BaseLLM
from math_rag.application.enums import LLMResponseFormat
from math_rag.application.models import LLMParams


class LLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def generate(self, prompt: str, params: LLMParams) -> str:
        match params.response_format:
            case LLMResponseFormat.TEXT:
                response_format = ResponseFormatText(type='text')

            case LLMResponseFormat.JSON_OBJECT:
                response_format = ResponseFormatJSONObject(type='json_object')

            case LLMResponseFormat.JSON_SCHEMA:
                response_format = ResponseFormatJSONSchema(
                    type='json_schema', json_schema=params.json_schema
                )

            case other:
                raise ValueError(f'Response format ${other} is not supported')

        completion = await self.client.chat.completions.create(
            model=params.model,
            messages=[{'role': 'user', 'content': prompt}],
            response_format=response_format,
            logprobs=params.logprobs,
            temperature=params.temperature,
            top_logprobs=params.top_logprobs,
        )

        return completion.choices[0].message.content
