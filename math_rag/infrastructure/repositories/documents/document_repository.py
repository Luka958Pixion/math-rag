from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, cast
from uuid import UUID

from bson.binary import UuidRepresentation
from bson.json_util import JSONOptions, dumps, loads
from pymongo import ASCENDING, AsyncMongoClient, InsertOne
from pymongo.results import DeleteResult

from math_rag.application.base.repositories.documents import BaseDocumentRepository
from math_rag.infrastructure.types.repositories.documents import (
    MappingType,
    SourceType,
    TargetType,
)
from math_rag.shared.utils import TypeUtil


BACKUP_PATH = Path(__file__).parents[4] / '.tmp' / 'backups' / 'mongo'


class DocumentRepository(
    BaseDocumentRepository[SourceType], Generic[SourceType, TargetType, MappingType]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = TypeUtil.get_type_args(self.__class__)
        self.source_cls = cast(type[SourceType], args[1][0])
        self.target_cls = cast(type[TargetType], args[1][1])
        self.mapping_cls = cast(type[MappingType], args[1][2])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = self.target_cls.__name__.lower()
        self.collection = self.db[self.collection_name]
        self.json_options = JSONOptions(uuid_representation=UuidRepresentation.STANDARD)

    async def insert_one(self, item: SourceType):
        doc = self.mapping_cls.to_target(item)
        bson_doc = doc.model_dump()

        await self.collection.insert_one(bson_doc)

    async def insert_many(self, items: list[SourceType]):
        docs = [self.mapping_cls.to_target(item) for item in items]
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def batch_insert_many(self, items: list[SourceType], *, batch_size: int):
        operations = []

        for item in items:
            doc = self.mapping_cls.to_target(item)
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def find_one(self, *, filter: dict[str, Any] | None = None) -> SourceType | None:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        bson_doc = await self.collection.find_one(filter)

        if bson_doc:
            doc = self.target_cls.model_validate(bson_doc)
            item = self.mapping_cls.to_source(doc)

            return item

        return None

    async def find_many(self, *, filter: dict[str, Any] | None = None) -> list[SourceType]:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        cursor = self.collection.find(filter)

        if 'timestamp' in self.target_cls.model_fields:
            cursor = cursor.sort('timestamp', ASCENDING)

        bson_docs = await cursor.to_list()

        docs = [self.target_cls.model_validate(bson_doc) for bson_doc in bson_docs]
        items = [self.mapping_cls.to_source(doc) for doc in docs]

        return items

    async def batch_find_many(
        self, *, batch_size: int, filter: dict[str, Any] | None = None
    ) -> AsyncGenerator[list[SourceType], None]:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        cursor = self.collection.find(filter)

        if 'timestamp' in self.target_cls.model_fields:
            cursor = cursor.sort('timestamp', ASCENDING)

        cursor = cursor.batch_size(batch_size)
        batch: list[SourceType] = []

        async for bson_doc in cursor:
            doc = self.target_cls.model_validate(bson_doc)
            batch.append(self.mapping_cls.to_source(doc))

            if len(batch) >= batch_size:
                yield batch

                batch = []

        if batch:
            yield batch

    async def delete_one(self, filter: dict[str, Any]) -> int:
        if 'id' in filter:
            filter['_id'] = filter.pop('id')

        delete_result = await self.collection.delete_one(filter)

        return delete_result.deleted_count

    async def delete_many(self, filter: dict[str, Any]) -> int:
        if 'id' in filter:
            filter['_id'] = filter.pop('id')

        delete_result = await self.collection.delete_many(filter)

        return delete_result.deleted_count

    async def clear(self) -> int:
        delete_result = await self.collection.delete_many({})

        return delete_result.deleted_count

    async def count(self, filter: dict[str, Any] | None = None) -> int:
        if not filter:
            filter = {}

        elif 'id' in filter:
            filter['_id'] = filter.pop('id')

        return await self.collection.count_documents(filter)

    async def exists(self, id: UUID) -> bool:
        return await self.collection.find_one({'_id': id}) is not None

    async def backup(self) -> Path:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_path = BACKUP_PATH / timestamp / f'{self.collection_name}.ndjson'
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        cursor = self.collection.find().batch_size(100)

        with open(backup_path, 'w') as file:
            async for document in cursor:
                file.write(dumps(document, json_options=self.json_options) + '\n')

        return backup_path

    async def restore(self, backup_path: Path):
        await self.clear()

        batch = []

        with open(backup_path, 'r') as file:
            for line in file:
                document = loads(line, json_options=self.json_options)
                batch.append(document)

                if len(batch) >= 100:
                    await self.collection.insert_many(batch)
                    batch.clear()

        if batch:
            await self.collection.insert_many(batch)
