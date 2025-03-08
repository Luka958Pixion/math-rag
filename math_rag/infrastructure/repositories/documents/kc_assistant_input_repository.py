from uuid import UUID

from pymongo import AsyncMongoClient, InsertOne

from math_rag.application.models.assistants import KCAssistantInput
from math_rag.infrastructure.models.documents import KCAssistantInputDocument


class KCAssistantInputRepository:
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = KCAssistantInput.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_many(self, items: list[KCAssistantInput]):
        docs = [KCAssistantInputDocument.from_internal(item) for item in items]
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def batch_insert_many(self, items: list[KCAssistantInput], batch_size: int):
        operations = []

        for item in items:
            doc = KCAssistantInputDocument.from_internal(item)
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def find_by_id(self, id: UUID) -> KCAssistantInput | None:
        bson_doc = await self.collection.find_one({'_id': id})

        if bson_doc:
            doc = KCAssistantInputDocument(**bson_doc)
            item = KCAssistantInputDocument.to_internal(doc)

            return item

        return None

    async def find_many(self, limit: int | None = None) -> list[KCAssistantInput]:
        cursor = self.collection.find()

        if limit:
            cursor = cursor.limit(limit)

        bson_docs = await cursor.to_list(length=limit)
        docs = [KCAssistantInputDocument(**bson_doc) for bson_doc in bson_docs]
        items = [KCAssistantInputDocument.to_internal(doc) for doc in docs]

        return items
