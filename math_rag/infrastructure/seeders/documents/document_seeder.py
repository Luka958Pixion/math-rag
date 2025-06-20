from typing import Generic, cast

from pymongo import AsyncMongoClient

from math_rag.application.base.seeders.documents import BaseDocumentSeeder
from math_rag.infrastructure.types.repositories.documents import TargetType
from math_rag.shared.utils import StrUtil, TypeUtil


class DocumentSeeder(BaseDocumentSeeder, Generic[TargetType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[0])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = StrUtil.to_snake_case(self.target_cls.__name__)

    async def seed(self, reset=False):
        if reset:
            await self._delete_collection()

        await self._create_collection()

    async def _create_collection(self):
        collection_names = await self.db.list_collection_names()

        if self.collection_name in collection_names:
            return

        await self.db.create_collection(self.collection_name)

    async def _delete_collection(self):
        collection_names = await self.db.list_collection_names()

        if self.collection_name in collection_names:
            await self.db[self.collection_name].drop()
