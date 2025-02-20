from openai import NOT_GIVEN, AsyncOpenAI


class LLM:
    def __init__(self, model: str, base_url: str = None, api_key: str = None):
        self.model = model
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    async def generate(self, prompt: str) -> str:
        use_json = True  # TODO

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            response_format={'type': 'json_object'} if use_json else NOT_GIVEN,
        )

        return completion.choices[0].message.content
