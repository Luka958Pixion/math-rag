from typing import Generic, cast, get_args
from uuid import UUID

from pymongo import AsyncMongoClient, InsertOne

from math_rag.infrastructure.types import DocumentType, InternalType


class CommonRepository(Generic[DocumentType, InternalType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = get_args(self.__orig_class__)

        if len(args) != 2:
            raise TypeError(f'Expected two type arguments, got {len(args)}: {args}')

        self.document_cls = cast(type[DocumentType], args[0])
        self.internal_cls = cast(type[InternalType], args[1])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = self.internal_cls.__name__.lower()
        self.collection = self.db[self.collection_name]

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
