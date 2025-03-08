from typing import Generic, cast, get_args

from pymongo import AsyncMongoClient

from math_rag.infrastructure.types import SourceType


class CommonSeeder(Generic[SourceType]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        args = get_args(self.__class__.__orig_bases__[0])

        if len(args) != 1:
            raise TypeError(f'Expected one type argument, got {len(args)}: {args}')

        self.source_cls = cast(type[SourceType], args[0])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = self.source_cls.__name__.lower()

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
