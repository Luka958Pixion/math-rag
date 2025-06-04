from typing import Generic, cast
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, PointStruct

from math_rag.application.base.repositories.embeddings import BaseEmbeddingRepository
from math_rag.infrastructure.types.repositories.embeddings import (
    MappingType,
    SourceType,
    TargetType,
)
from math_rag.shared.utils import TypeUtil


class EmbeddingRepository(
    BaseEmbeddingRepository[SourceType], Generic[SourceType, TargetType, MappingType]
):
    def __init__(self, client: AsyncQdrantClient):
        args = TypeUtil.get_type_args(self.__class__)
        self.source_cls = cast(type[SourceType], args[1][0])
        self.target_cls = cast(type[TargetType], args[1][1])
        self.mapping_cls = cast(type[MappingType], args[1][2])

        # self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.client = client
        self.collection_name = self.target_cls.__name__.lower()

    async def upsert_one(self, item: SourceType):
        point = PointStruct(
            id=str(model.id),
            vector=model.embedding,
            payload=model.metadata,
        )
        await self.client.upsert(collection_name=self.collection_name, points=[point])

    async def upsert_many(self, items: list[SourceType]):
        points = [
            PointStruct(
                id=str(item.id),
                vector=item.embedding,
                payload=item.metadata,
            )
            for item in items
        ]
        await self.client.upsert(collection_name=self.collection_name, points=points)

    async def batch_upsert_many(self, items: list[SourceType], *, batch_size: int):
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            points = [
                PointStruct(
                    id=str(m.id),
                    vector=m.embedding,
                    payload=m.metadata,
                )
                for m in batch
            ]
            await self.client.upsert(collection_name=self.collection_name, points=points)

    async def search(self, embedding: list[float], top_k: int) -> list[TargetType]:
        # TODO filtering
        filter = None

        qdrant_filter = Filter(**filter) if filter is not None else None
        response = await self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=True,
            filter=qdrant_filter,
        )
        results = []

        for hit in response:
            results.append(
                DocumentDBModel(id=UUID(hit.id), embedding=hit.vector, metadata=hit.payload or {})
            )

        return results
