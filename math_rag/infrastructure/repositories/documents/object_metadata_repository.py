from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from bson.binary import UuidRepresentation
from bson.json_util import JSONOptions, dumps, loads
from pymongo import ASCENDING, AsyncMongoClient, InsertOne

from math_rag.infrastructure.models.documents import ObjectMetadataDocument


BACKUP_PATH = Path(__file__).parents[4] / '.tmp' / 'backups' / 'mongo'


class ObjectMetadataRepository:
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = ObjectMetadataDocument.__name__.lower()
        self.collection = self.db[self.collection_name]
        self.json_options = JSONOptions(uuid_representation=UuidRepresentation.STANDARD)

    async def insert_one(self, doc: ObjectMetadataDocument):
        bson_doc = doc.model_dump()

        await self.collection.insert_one(bson_doc)

    async def insert_many(self, docs: list[ObjectMetadataDocument]):
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def batch_insert_many(self, docs: list[ObjectMetadataDocument], *, batch_size: int):
        operations = []

        for doc in docs:
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def find_one(
        self, *, filter: dict[str, Any] | None = None
    ) -> ObjectMetadataDocument | None:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        bson_doc = await self.collection.find_one(filter)

        return ObjectMetadataDocument.model_validate(bson_doc) if bson_doc else None

    async def find_many(
        self, *, filter: dict[str, Any] | None = None
    ) -> list[ObjectMetadataDocument]:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        cursor = self.collection.find(filter).sort('timestamp', ASCENDING)
        bson_docs = await cursor.to_list()

        return [ObjectMetadataDocument.model_validate(bson_doc) for bson_doc in bson_docs]

    async def batch_find_many(
        self, *, batch_size: int, filter: dict[str, Any] | None = None
    ) -> AsyncGenerator[list[ObjectMetadataDocument], None]:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        cursor = self.collection.find(filter).sort('timestamp', ASCENDING).batch_size(batch_size)
        batch: list[ObjectMetadataDocument] = []

        async for bson_doc in cursor:
            doc = ObjectMetadataDocument.model_validate(bson_doc)
            batch.append(doc)

            if len(batch) >= batch_size:
                yield batch

                batch = []

        if batch:
            yield batch

    async def clear(self):
        await self.collection.delete_many({})

    async def count(self, filter: dict[str, Any] | None = None) -> int:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        return await self.collection.count_documents(filter)

    async def exists(self, id: UUID) -> bool:
        return await self.collection.find_one({'_id': id}) is not None

    async def backup(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.backup_file_path = BACKUP_PATH / timestamp / f'{self.collection_name}.ndjson'
        self.backup_file_path.parent.mkdir(parents=True, exist_ok=True)

        cursor = self.collection.find().batch_size(100)

        with open(self.backup_file_path, 'w') as file:
            async for document in cursor:
                file.write(dumps(document, json_options=self.json_options) + '\n')

    async def restore(self):
        await self.clear()

        batch = []

        with open(self.backup_file_path, 'r') as file:
            for line in file:
                document = loads(line, json_options=self.json_options)
                batch.append(document)

                if len(batch) >= 100:
                    await self.collection.insert_many(batch)
                    batch.clear()

        if batch:
            await self.collection.insert_many(batch)
