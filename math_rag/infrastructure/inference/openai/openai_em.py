from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseEM


class OpenAIEM(BaseEM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def embed(self, text: str, model: str) -> list[float]:
        response = await self.client.embeddings.create(
            input=text, model=model, encoding_format='float'
        )

        return response.data[0].embedding
