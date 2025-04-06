from typing import AsyncGenerator

from math_rag.infrastructure.constants.utils import CHUNK_SIZE


class BytesStreamerUtil:
    async def stream_bytes(data: bytes) -> AsyncGenerator[bytes, None]:
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i : i + CHUNK_SIZE]

            yield chunk
