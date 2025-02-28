from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionPrediction


class MathExpressionPredictionSeeder:
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpressionPrediction.__name__.lower()

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
