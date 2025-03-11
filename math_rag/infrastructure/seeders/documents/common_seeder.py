from typing import Generic, cast

from pymongo import AsyncMongoClient

from math_rag.infrastructure.types import TargetType
from math_rag.shared.utils import TypeArgUtil


class CommonSeeder(Generic[TargetType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = TypeArgUtil.get_type_arg(self.__class__)
        self.target_cls = cast(type[TargetType], args[0])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = self.target_cls.__name__.lower()

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
