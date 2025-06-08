from typing import Generic, cast
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct

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

        self.client = client
        self.collection_name = self.target_cls.__name__.lower()

    async def upsert_one(self, item: SourceType, embedding: list[float]):
        point = PointStruct(**self.mapping_cls.to_target(item, embedding=embedding).model_dump())

        await self.client.upsert(collection_name=self.collection_name, points=[point])

    async def upsert_many(self, items: list[SourceType], embeddings: list[list[float]]):
        points = [
            PointStruct(**self.mapping_cls.to_target(item, embedding=embedding).model_dump())
            for item, embedding in zip(items, embeddings)
        ]

        await self.client.upsert(collection_name=self.collection_name, points=points)

    async def find_one(self, id: UUID) -> SourceType | None:
        records = await self.client.retrieve(collection_name=self.collection_name, ids=[str(id)])

        if not records:
            return None

        return self.mapping_cls.to_source(self.target_cls(**records[0].model_dump()))

    async def find_many(self, ids: list[UUID]) -> list[SourceType]:
        records = await self.client.retrieve(
            collection_name=self.collection_name, ids=[str(id) for id in ids]
        )

        return [
            self.mapping_cls.to_source(self.target_cls(**record.model_dump())) for record in records
        ]

    async def search(self, embedding: list[float], *, limit: int) -> list[SourceType]:
        scored_points = await self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=limit,
            with_payload=True,
            with_vectors=False,
            filter=None,
        )

        return [
            self.mapping_cls.to_source(self.target_cls(**scored_point.model_dump()))
            for scored_point in scored_points
        ]
