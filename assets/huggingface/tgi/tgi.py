from asyncio import run
from pathlib import Path
from typing import cast

from decouple import config
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.inference._generated.types.chat_completion import (
    ChatCompletionOutput,
)


async def main():
    ROOT = Path(...)  # TODO /lustre/user...
    TGI_BASE_URL = config('TGI_BASE_URL')

    request = ...
    client = AsyncInferenceClient(base_url=..., api_key=...)

    input_file_path = Path(...)
    output_file_path = Path(...)

    # TODO concurrency

    try:
        output = await client.chat_completion(
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
        output = cast(ChatCompletionOutput, output)

    except Exception as e:
        pass


if __name__ == '__main__':
    run(main())
