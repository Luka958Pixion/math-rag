from typing import Generic, cast
from uuid import UUID

from pymongo import AsyncMongoClient, InsertOne

from math_rag.infrastructure.types import MappingType, SourceType, TargetType
from math_rag.shared.utils import TypeUtil


class DocumentRepository(Generic[SourceType, TargetType, MappingType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = TypeUtil.get_type_args(self.__class__)
        self.source_cls = cast(type[SourceType], args[0])
        self.target_cls = cast(type[TargetType], args[1])
        self.mapping_cls = cast(type[MappingType], args[2])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = self.target_cls.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_one(self, item: SourceType):
        doc = self.mapping_cls.to_target(item)
        bson_doc = doc.model_dump()

        await self.collection.insert_one(bson_doc)

    async def insert_many(self, items: list[SourceType]):
        docs = [self.mapping_cls.to_target(item) for item in items]
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def batch_insert_many(self, items: list[SourceType], batch_size: int):
        operations = []

        for item in items:
            doc = self.mapping_cls.to_target(item)
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def find_by_id(self, id: UUID) -> SourceType | None:
        bson_doc = await self.collection.find_one({'_id': id})

        if bson_doc:
            doc = self.target_cls(**bson_doc)
            item = self.mapping_cls.to_source(doc)

            return item

        return None

    async def find_many(self, limit: int | None = None) -> list[SourceType]:
        cursor = self.collection.find()

        if limit:
            cursor = cursor.limit(limit)

        bson_docs = await cursor.to_list(length=limit)
        docs = [self.target_cls(**bson_doc) for bson_doc in bson_docs]
        items = [self.mapping_cls.to_source(doc) for doc in docs]

        return items
