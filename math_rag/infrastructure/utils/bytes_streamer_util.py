from typing import AsyncGenerator

from math_rag.infrastructure.constants.utils import CHUNK_SIZE


class BytesStreamerUtil:
    async def stream(source: bytes) -> AsyncGenerator[bytes, None]:
        for i in range(0, len(source), CHUNK_SIZE):
            chunk = source[i : i + CHUNK_SIZE]

            yield chunk
