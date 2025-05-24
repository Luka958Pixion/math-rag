from typing import Any, Generic, cast
from uuid import UUID

from pymongo import AsyncMongoClient, UpdateOne

from math_rag.infrastructure.types.repositories.documents import TargetType
from math_rag.shared.utils import TypeUtil


class DocumentMigration(Generic[TargetType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[1][0])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = self.target_cls.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def add_field(self, field: str, id_to_field_value: dict[UUID, Any]):
        if not id_to_field_value:
            return

        write_operations = [
            UpdateOne({'_id': id}, {'$set': {field: filed_value}})
            for id, filed_value in id_to_field_value.items()
        ]

        if write_operations:
            await self.collection.bulk_write(write_operations)

    async def remove_field(self, field: str):
        await self.collection.update_many({}, {'$unset': {field: ''}})
