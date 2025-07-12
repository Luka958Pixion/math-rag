from typing import Any, Generic, cast
from uuid import UUID

from pymongo import ASCENDING, AsyncMongoClient, UpdateOne

from math_rag.infrastructure.types.repositories.documents import TargetType
from math_rag.shared.utils import StrUtil, TypeUtil


class DocumentMigration(Generic[TargetType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[0])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = StrUtil.to_snake_case(self.target_cls.__name__)
        self.collection = self.db[self.collection_name]

    async def add_field(
        self,
        field: str,
        *,
        create_index: bool,
        id_to_value: dict[UUID, Any] | None = None,
        default_value: Any | None = None,
    ):
        if id_to_value:
            write_operations = [
                UpdateOne({'_id': id}, {'$set': {field: value}})
                for id, value in id_to_value.items()
            ]

            if write_operations:
                await self.collection.bulk_write(write_operations)

        else:
            await self.collection.update_many({}, {'$set': {field: default_value}})

        if create_index:
            await self.collection.create_index([(field, ASCENDING)])

    async def remove_field(self, field: str):
        await self.collection.update_many({}, {'$unset': {field: ''}})
