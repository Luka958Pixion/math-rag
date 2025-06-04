from typing import Generic, cast

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, HnswConfigDiff, VectorParams

from math_rag.application.base.seeders.embeddings import BaseEmbeddingSeeder
from math_rag.infrastructure.types.repositories.embeddings import TargetType
from math_rag.shared.utils import TypeUtil


class EmbeddingSeeder(BaseEmbeddingSeeder, Generic[TargetType]):
    def __init__(self, client: AsyncQdrantClient):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[0])

        self.client = client
        self.collection_name = self.target_cls.__name__.lower()

    async def seed(self, reset=False):
        if reset:
            await self._delete_collection()

        await self._create_collection()

    async def _create_collection(self):
        if await self.client.collection_exists(collection_name=self.collection_name):
            return

        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(
                    m=48,
                    ef_construct=256,
                ),
            ),
        )

    async def _delete_collection(self):
        self.client.delete_collection(collection_name=self.collection_name)
