from asyncio import run
from pathlib import Path

from decouple import config
from text_generation import AsyncClient


async def main():
    ROOT = Path(...)  # TODO /lustre/user...
    TGI_BASE_URL = config('TGI_BASE_URL')
    client = AsyncClient(TGI_BASE_URL)
    prompt = 'Tell me a joke.'
    response = await client.generate(prompt, max_new_tokens=50)
    print(response.generated_text)


if __name__ == '__main__':
    run(main())
