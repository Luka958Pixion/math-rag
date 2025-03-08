from typing import Generic
from uuid import UUID

from pymongo import AsyncMongoClient, InsertOne

from math_rag.infrastructure.types import DocumentType, InternalType


class CommonRepository(Generic[DocumentType, InternalType]):
    document_cls: type[DocumentType]

    def __init__(
        self,
        client: AsyncMongoClient,
        deployment: str,
        document_cls: type[DocumentType],
        internal_cls: type[InternalType],
    ):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = internal_cls.__name__.lower()
        self.collection = self.db[self.collection_name]
        self.document_cls = document_cls

    async def insert_many(self, items: list[InternalType]):
        docs = [self.document_cls.from_internal(item) for item in items]
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def batch_insert_many(self, items: list[InternalType], batch_size: int):
        operations = []

        for item in items:
            doc = self.document_cls.from_internal(item)
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def find_by_id(self, id: UUID) -> InternalType | None:
        bson_doc = await self.collection.find_one({'_id': id})

        if bson_doc:
            doc = self.document_cls(**bson_doc)
            item = self.document_cls.to_internal(doc)

            return item

        return None

    async def find_many(self, limit: int | None = None) -> list[InternalType]:
        cursor = self.collection.find()

        if limit:
            cursor = cursor.limit(limit)

        bson_docs = await cursor.to_list(length=limit)
        docs = [self.document_cls(**bson_doc) for bson_doc in bson_docs]
        items = [self.document_cls.to_internal(doc) for doc in docs]

        return items
