from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionClassification


class MathExpressionClassificationRepository:
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpressionClassification.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_math_expression_predictions(
        self, items: list[MathExpressionClassification]
    ):
        docs = [item.model_dump() for item in items]

        for doc in docs:
            doc['_id'] = doc.pop('id')

        await self.collection.insert_many(docs)

    async def get_math_expression_predictions(
        self, limit: int
    ) -> list[MathExpressionClassification]:
        cursor = self.collection.find().limit(limit)
        docs = await cursor.to_list(length=limit)

        for doc in docs:
            doc['id'] = doc.pop('_id')

        return [MathExpressionClassification(**doc) for doc in docs]
