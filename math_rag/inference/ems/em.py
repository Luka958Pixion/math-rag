from openai import AsyncOpenAI


class EM:
    def __init__(self, model: str, base_url: str = None, api_key: str = None):
        self.model = model
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    async def a_embed_text(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            input=text, model=self.model, encoding_format='float'
        )

        return response.data[0].embedding

    async def a_embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            input=texts, model=self.model, encoding_format='float'
        )

        return [x.embedding for x in response.data]
