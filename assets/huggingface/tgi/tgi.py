from asyncio import run
from pathlib import Path

from decouple import config
from huggingface_hub import AsyncInferenceClient


async def main():
    ROOT = Path(...)  # TODO /lustre/user...
    TGI_BASE_URL = config('TGI_BASE_URL')

    request = ...
    client = AsyncInferenceClient(base_url=..., api_key=...)

    output = client.chat.completions.create(
        model=...,
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Count to 10'},
        ],
        n=...,
        logprobs=...,
        top_logprobs=...,
        response_format=...,
        temperature=...,
        max_tokens=1024,
    )


if __name__ == '__main__':
    run(main())
