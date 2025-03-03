from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseLLM, TBaseLLMResponseModel
from math_rag.application.models import LLMParams


class LLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def generate_text(self, prompt: str, params: LLMParams) -> str:
        completion = await self.client.chat.completions.create(
            model=params.model,
            messages=[{'role': 'user', 'content': prompt}],
            response_format={'type': 'text'},
            logprobs=params.logprobs,
            temperature=params.temperature,
            top_logprobs=params.top_logprobs,
        )

        return completion.choices[0].message.content

    async def generate_json(
        self,
        prompt: str,
        params: LLMParams,
        response_model_type: type[TBaseLLMResponseModel],
    ) -> TBaseLLMResponseModel:
        completion = await self.client.beta.chat.completions.parse(
            model=params.model,
            messages=[{'role': 'user', 'content': prompt}],
            response_format=response_model_type,
            logprobs=params.logprobs,
            temperature=params.temperature,
            top_logprobs=params.top_logprobs,
        )

        return completion.choices[0].message.parsed
