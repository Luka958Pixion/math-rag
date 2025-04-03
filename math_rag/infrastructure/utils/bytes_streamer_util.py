from typing import AsyncGenerator


CHUNK_SIZE = 8192


class BytesStreamerUtil:
    async def stream_bytes(data: bytes) -> AsyncGenerator[bytes, None]:
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i : i + CHUNK_SIZE]

            yield chunk
