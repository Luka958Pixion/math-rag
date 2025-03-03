from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from math_rag.application.base.repositories.embeddings import BaseEmbeddingRepository


class QdrantEmbeddingRepository(BaseEmbeddingRepository):
    def __init__(self, url: str):
        self.client = AsyncQdrantClient(url=url)

    async def create_collection(self, name: str):
        if await self.client.collection_exists(name):
            return

        await self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=100, distance=Distance.COSINE),
        )

    async def delete_collection(self, name: str):
        await self.client.delete_collection(name)
