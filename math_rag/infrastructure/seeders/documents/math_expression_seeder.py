from pymongo import AsyncMongoClient

from math_rag.application.base.seeders.documents import MathExpressionBaseSeeder
from math_rag.core.models import MathExpression


class MathExpressionSeeder(MathExpressionBaseSeeder):
    def __init__(self, host: str, deployment: str):
        self.client = AsyncMongoClient(host, uuidRepresentation='standard')
        self.db = self.client[deployment]
        self.collection_name = MathExpression.__name__.lower()

    async def seed(self):
        collection_names = await self.db.list_collection_names()

        if self.collection_name not in collection_names:
            await self.db.create_collection(self.collection_name)
